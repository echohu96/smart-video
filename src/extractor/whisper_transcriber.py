"""
Whisper 转录器
使用 OpenAI Whisper 进行语音转文字
"""

import os
import sys
import time
import threading
import atexit
import resource
from pathlib import Path
from typing import Optional
import whisper
from ..utils.logger import get_logger
from ..utils.config import get_settings
from ..utils.exceptions import TranscriptionError
from ..utils.file_manager import cleanup_temp_file

logger = get_logger(__name__)


class WhisperTranscriber:
    """Whisper 转录器"""
    
    def __init__(self, model_name: Optional[str] = None):
        """
        初始化 Whisper 转录器
        
        Args:
            model_name: Whisper 模型名称（tiny/base/small/medium/large）
        """
        self.settings = get_settings()
        self.model_name = model_name or self.settings.whisper_model
        self._model = None
    
    def _load_model(self):
        """加载 Whisper 模型（懒加载）"""
        if self._model is None:
            logger.info(f"加载 Whisper 模型: {self.model_name}")
            try:
                self._model = whisper.load_model(self.model_name)
                logger.info(f"Whisper 模型加载成功")
                # 验证模型是否真的加载成功
                if self._model is None:
                    raise TranscriptionError(f"模型加载后为 None: {self.model_name}")
            except Exception as e:
                logger.error(f"Whisper 模型加载失败: {e}", exc_info=True)
                raise TranscriptionError(f"无法加载 Whisper 模型: {e}")
    
    def transcribe(
        self,
        audio_file: str,
        language: Optional[str] = None,
        cleanup: bool = True
    ) -> str:
        """
        转录音频文件
        
        Args:
            audio_file: 音频文件路径
            language: 语言代码（可选，如 'zh', 'en'）
            cleanup: 转录后是否删除音频文件
        
        Returns:
            转录文本
        
        Raises:
            TranscriptionError: 转录失败
        """
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"音频文件不存在: {audio_file}")
        
        try:
            logger.info(f"开始转录音频: {audio_file}")
            logger.info(f"使用模型: {self.model_name}")
            
            # 懒加载模型
            self._load_model()
            
            # 执行转录
            logger.info("执行 Whisper 转录（这可能需要几分钟，请耐心等待）...")
            logger.info(f"音频文件: {audio_file}, 语言: {language or 'auto'}")
            
            # 确保输出不被缓冲
            import sys
            import os as os_module
            
            # 确保 stderr 不被缓冲 - 这是关键！
            if hasattr(sys.stderr, 'reconfigure'):
                try:
                    sys.stderr.reconfigure(line_buffering=True, encoding='utf-8')
                except Exception as e:
                    logger.debug(f"无法重新配置 stderr: {e}")
            
            # 强制刷新所有输出
            sys.stdout.flush()
            sys.stderr.flush()
            
            # 使用 print 直接输出提示（不通过 logger，避免被拦截）
            # 同时输出到 stdout 和 stderr，确保能看到
            print("\n" + "="*80, file=sys.stderr, flush=True)
            print("[Whisper 转录进行中... 进度会实时显示]", file=sys.stderr, flush=True)
            print("="*80 + "\n", file=sys.stderr, flush=True)
            
            # 验证模型是否已加载
            if self._model is None:
                raise TranscriptionError("Whisper 模型未加载，无法进行转录")
            
            # 验证音频文件
            if not os.path.exists(audio_file):
                raise FileNotFoundError(f"音频文件不存在: {audio_file}")
            
            # 检查音频文件大小
            file_size = os.path.getsize(audio_file)
            logger.info(f"音频文件大小: {file_size / 1024 / 1024:.2f} MB")
            if file_size == 0:
                raise TranscriptionError(f"音频文件为空: {audio_file}")
            
            # 执行转录，启用详细输出
            # 注意：verbose=True 会将进度输出到 stderr，需要确保不被缓冲
            try:
                logger.info("开始调用 Whisper transcribe 方法...")
                logger.info(f"模型类型: {type(self._model)}")
                logger.info(f"音频文件路径: {audio_file}")
                logger.info(f"语言设置: {language or 'auto'}")
                
                # 添加信号处理，捕获可能的终止信号
                import signal
                def signal_handler(signum, frame):
                    logger.warning(f"收到信号 {signum}，转录可能被中断")
                    print(f"\n[收到信号 {signum}，转录被中断]\n", file=sys.stderr, flush=True)
                    raise TranscriptionError(f"转录被信号 {signum} 中断")
                
                # 注册信号处理器
                old_handler = signal.signal(signal.SIGTERM, signal_handler)
                old_handler_int = signal.signal(signal.SIGINT, signal_handler)
                
                # 添加心跳日志线程，定期输出日志，确保程序还在运行
                heartbeat_stop = threading.Event()
                
                def heartbeat_logger():
                    """定期输出心跳日志"""
                    count = 0
                    while not heartbeat_stop.is_set():
                        time.sleep(30)  # 每30秒输出一次
                        if not heartbeat_stop.is_set():
                            count += 1
                            elapsed_seconds = count * 30
                            logger.info(f"[心跳] 转录仍在进行中... (已等待 {elapsed_seconds} 秒 / {elapsed_seconds/60:.1f} 分钟)")
                            print(f"[{time.strftime('%H:%M:%S')}] [心跳] 转录仍在进行中... (已等待 {elapsed_seconds} 秒)", file=sys.stderr, flush=True)
                
                heartbeat_thread = threading.Thread(target=heartbeat_logger, daemon=True)
                heartbeat_thread.start()
                
                try:
                    # 直接调用 transcribe，verbose=True 会输出进度到 stderr
                    logger.info("正在调用 model.transcribe()...")
                    logger.info("提示：转录可能需要几分钟，请耐心等待...")
                    logger.info("提示：如果长时间没有输出，请检查系统资源（CPU/内存）")
                    
                    # 记录开始时间
                    start_time = time.time()
                    logger.info(f"转录开始时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
                    
                    # 输出到 stderr，确保用户能看到
                    print(f"[{time.strftime('%H:%M:%S')}] 开始转录...", file=sys.stderr, flush=True)
                    sys.stdout.flush()
                    sys.stderr.flush()
                    
                    try:
                        result = self._model.transcribe(
                            audio_file,
                            language=language,
                            verbose=True,  # 显示转录进度（输出到 stderr）
                            fp16=False,  # CPU 上使用 FP32
                            task="transcribe"
                        )
                    except Exception as transcribe_error:
                        # 捕获 transcribe 内部的异常
                        elapsed = time.time() - start_time
                        logger.error(f"model.transcribe() 内部出错 (运行了 {elapsed:.1f} 秒): {transcribe_error}", exc_info=True)
                        print(f"[错误] model.transcribe() 内部出错: {transcribe_error}", file=sys.stderr, flush=True)
                        raise
                    
                    # 停止心跳线程
                    heartbeat_stop.set()
                    heartbeat_thread.join(timeout=1)
                    
                    # 记录结束时间
                    end_time = time.time()
                    elapsed = end_time - start_time
                    logger.info(f"model.transcribe() 调用完成")
                    logger.info(f"转录结束时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
                    logger.info(f"转录耗时: {elapsed:.1f} 秒 ({elapsed/60:.1f} 分钟)")
                    print(f"[{time.strftime('%H:%M:%S')}] 转录完成，耗时 {elapsed:.1f} 秒 ({elapsed/60:.1f} 分钟)", file=sys.stderr, flush=True)
                    
                    # 验证结果
                    if result is None:
                        raise TranscriptionError("转录结果为空（None）")
                    if not isinstance(result, dict):
                        raise TranscriptionError(f"转录结果格式错误: {type(result)}")
                    
                    # 再次刷新输出
                    sys.stdout.flush()
                    sys.stderr.flush()
                    
                    print("\n" + "="*80, file=sys.stderr, flush=True)
                    print("[Whisper 转录完成]", file=sys.stderr, flush=True)
                    print("="*80 + "\n", file=sys.stderr, flush=True)
                    logger.info("转录处理完成")
                finally:
                    # 恢复原始信号处理器
                    signal.signal(signal.SIGTERM, old_handler)
                    signal.signal(signal.SIGINT, old_handler_int)
                    
            except KeyboardInterrupt:
                print("\n[转录被用户中断]\n", file=sys.stderr, flush=True)
                logger.warning("转录被用户中断 (KeyboardInterrupt)")
                sys.stdout.flush()
                sys.stderr.flush()
                raise
            except SystemExit as e:
                print(f"\n[系统退出: {e}]\n", file=sys.stderr, flush=True)
                logger.warning(f"系统退出: {e}")
                sys.stdout.flush()
                sys.stderr.flush()
                raise
            except MemoryError as e:
                error_msg = f"内存不足: {type(e).__name__}: {e}"
                print(f"\n[严重错误] {error_msg}\n", file=sys.stderr, flush=True)
                logger.error(f"内存不足错误: {e}", exc_info=True)
                sys.stdout.flush()
                sys.stderr.flush()
                raise TranscriptionError(f"内存不足，无法完成转录: {e}")
            except OSError as e:
                error_msg = f"系统错误: {type(e).__name__}: {e}"
                print(f"\n[系统错误] {error_msg}\n", file=sys.stderr, flush=True)
                logger.error(f"系统错误: {e}", exc_info=True)
                sys.stdout.flush()
                sys.stderr.flush()
                raise TranscriptionError(f"系统错误: {e}")
            except Exception as e:
                # 详细错误信息
                import traceback
                error_type = type(e).__name__
                error_msg = str(e)
                full_error = f"转录出错: {error_type}: {error_msg}"
                print(f"\n[错误] {full_error}\n", file=sys.stderr, flush=True)
                print("="*80, file=sys.stderr, flush=True)
                print("详细错误堆栈:", file=sys.stderr, flush=True)
                print(traceback.format_exc(), file=sys.stderr, flush=True)
                print("="*80, file=sys.stderr, flush=True)
                logger.error(f"转录过程中出错: {error_type}: {error_msg}", exc_info=True)
                sys.stdout.flush()
                sys.stderr.flush()
                raise
            
            # 提取文本
            text = result.get('text', '').strip()
            
            if not text:
                raise TranscriptionError("转录结果为空")
            
            logger.info(f"转录成功，文本长度: {len(text)} 字符")
            
            # 清理临时音频文件
            if cleanup:
                logger.debug(f"清理临时音频文件: {audio_file}")
                cleanup_temp_file(audio_file)
            
            return text
        
        except FileNotFoundError as e:
            logger.error(f"文件未找到: {e}")
            raise
        except TranscriptionError:
            # TranscriptionError 已经包含详细错误信息，直接抛出
            raise
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            logger.error(f"转录失败: {error_type}: {error_msg}", exc_info=True)
            print(f"[严重错误] 转录失败: {error_type}: {error_msg}", file=sys.stderr, flush=True)
            # 即使转录失败，也尝试清理临时文件
            if cleanup:
                logger.info("清理临时音频文件...")
                cleanup_temp_file(audio_file)
            raise TranscriptionError(f"转录失败: {error_type}: {error_msg}")
    
    def transcribe_with_segments(
        self,
        audio_file: str,
        language: Optional[str] = None,
        cleanup: bool = True
    ) -> dict:
        """
        转录音频文件，返回详细结果（包含时间戳）
        
        Args:
            audio_file: 音频文件路径
            language: 语言代码
            cleanup: 转录后是否删除音频文件
        
        Returns:
            包含文本和分段信息的字典
        
        Raises:
            TranscriptionError: 转录失败
        """
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"音频文件不存在: {audio_file}")
        
        try:
            logger.info(f"开始转录音频（带时间戳）: {audio_file}")
            
            # 懒加载模型
            self._load_model()
            
            # 执行转录
            logger.info("执行 Whisper 转录（这可能需要几分钟，请耐心等待）...")
            logger.info(f"音频文件: {audio_file}, 语言: {language or 'auto'}")
            
            # 确保输出不被缓冲
            import sys
            import os as os_module
            
            # 确保 stderr 不被缓冲
            if hasattr(sys.stderr, 'reconfigure'):
                try:
                    sys.stderr.reconfigure(line_buffering=True)
                except Exception:
                    pass
            
            sys.stdout.flush()
            sys.stderr.flush()
            
            # 使用 print 直接输出提示（不通过 logger，避免被拦截）
            print("\n[Whisper 转录进行中... 进度会实时显示]\n", file=sys.stderr, flush=True)
            
            # 执行转录，启用详细输出
            try:
                result = self._model.transcribe(
                    audio_file,
                    language=language,
                    verbose=True,  # 显示转录进度（输出到 stderr）
                    fp16=False,  # CPU 上使用 FP32
                    task="transcribe"
                )
                
                # 再次刷新输出
                sys.stdout.flush()
                sys.stderr.flush()
                
                print("\n[Whisper 转录完成]\n", file=sys.stderr, flush=True)
                logger.info("转录处理完成")
            except KeyboardInterrupt:
                print("\n[转录被用户中断]\n", file=sys.stderr, flush=True)
                logger.warning("转录被用户中断")
                raise
            except Exception as e:
                print(f"\n[转录出错: {e}]\n", file=sys.stderr, flush=True)
                logger.error(f"转录过程中出错: {e}", exc_info=True)
                sys.stdout.flush()
                sys.stderr.flush()
                raise
            
            # 提取文本和分段
            text = result.get('text', '').strip()
            segments = result.get('segments', [])
            
            if not text:
                raise TranscriptionError("转录结果为空")
            
            logger.info(f"转录成功，文本长度: {len(text)} 字符，分段数: {len(segments)}")
            
            # 清理临时音频文件
            if cleanup:
                cleanup_temp_file(audio_file)
            
            return {
                'text': text,
                'segments': segments,
                'language': result.get('language', language),
            }
        
        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"转录失败: {e}", exc_info=True)
            if cleanup:
                cleanup_temp_file(audio_file)
            raise TranscriptionError(f"转录失败: {e}")
