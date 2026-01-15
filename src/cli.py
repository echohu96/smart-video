"""
CLI 接口
使用 Click 实现命令行界面
"""

import os
import sys
from pathlib import Path
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text

from .utils.logger import get_logger
from .utils.file_manager import get_output_dir
from .utils.platform_detector import PlatformDetector, VideoPlatform
from .utils.exceptions import (
    SmartVideoError,
    SubtitleNotFoundError,
    DownloadError,
    AIAPIError,
    TranscriptionError,
    PlatformNotSupportedError,
)
from .downloader.youtube import YouTubePlatform
from .extractor.content_extractor import ContentExtractor
from .extractor.whisper_transcriber import WhisperTranscriber
from .ai.summarizer import Summarizer
from .generator.md_generator import MarkdownGenerator

logger = get_logger(__name__)
# 创建 Console，使用默认设置（Rich 默认会处理 stdout 和 stderr）
# 但我们需要让 Whisper 的 stderr 输出直接显示，所以不使用 Rich 的 stderr 捕获
console = Console()


def _sanitize_filename(filename: str, max_length: int = 100) -> str:
    """
    清理文件名，移除特殊字符
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    filename = filename.strip(' .')

    if len(filename) > max_length:
        filename = filename[:max_length]

    if not filename:
        filename = "video_transcript"

    return filename


def _resolve_transcript_output_path(output: str | None, title: str) -> Path:
    output_dir = get_output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)

    if output:
        output_path = Path(output)
        if not output_path.is_absolute():
            output_path = output_dir / output_path
    else:
        safe_title = _sanitize_filename(title)
        output_path = output_dir / f"{safe_title}.txt"

    if output_path.exists():
        base_name = output_path.stem
        suffix = output_path.suffix or ".txt"
        counter = 1
        while output_path.exists():
            output_path = output_path.with_name(f"{base_name}_{counter}{suffix}")
            counter += 1

    return output_path


def _write_transcript(text_content: str, metadata, output: str | None) -> Path:
    output_path = _resolve_transcript_output_path(output, metadata.title)
    header_lines = [
        f"Title: {metadata.title}",
        f"Author: {metadata.author}",
        f"Duration: {metadata.duration // 60} min",
        f"URL: {metadata.url}",
        "",
    ]
    content = "\n".join(header_lines) + text_content
    output_path.write_text(content, encoding="utf-8")
    return output_path


def process_video(
    url: str,
    output: str = None,
    ai_provider: str = None,
    use_whisper: bool = False,
    force_whisper: bool = False,
    no_cache: bool = False,
    skip_summary: bool = False,
):
    """
    处理视频，生成总结
    
    Args:
        url: 视频 URL
        output: 输出文件路径
        ai_provider: AI 提供商
        use_whisper: 是否使用 Whisper（无字幕时）
        force_whisper: 强制使用 Whisper（即使有字幕）
        no_cache: 禁用缓存
        skip_summary: 仅保存转录文本，不生成总结
    """
    try:
        # 检测平台
        console.print(f"[bold blue]检测视频平台...[/bold blue]")
        platform_type = PlatformDetector.detect(url)
        
        if platform_type != VideoPlatform.YOUTUBE:
            raise PlatformNotSupportedError(f"当前仅支持 YouTube 平台")
        
        console.print(f"[green]✓[/green] 平台: YouTube")
        
        # 创建平台实例
        platform = YouTubePlatform()
        
        # 提取元数据
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("提取视频元数据...", total=None)
            metadata = platform.extract_metadata(url)
            progress.update(task, completed=True)
        
        console.print(f"[green]✓[/green] 视频: {metadata.title}")
        console.print(f"[green]✓[/green] 作者: {metadata.author}")
        console.print(f"[green]✓[/green] 时长: {metadata.duration // 60} 分钟")
        
        # 下载字幕或转录
        text_content = None
        subtitle_file = None
        
        if force_whisper:
            # 强制使用 Whisper
            console.print(f"[bold yellow]强制使用 Whisper 转录...[/bold yellow]")
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("下载音频文件...", total=None)
                audio_file = platform.download_audio(url)
                progress.update(task, completed=True)
            
            console.print(f"[green]✓[/green] 音频下载完成")
            
            console.print("[yellow]提示:[/yellow] Whisper 转录可能需要几分钟，请耐心等待...")
            console.print("[dim]转录进度会实时显示在下方（实时输出）[/dim]")
            console.print("")
            
            # 确保输出不被缓冲
            import sys
            import os
            os.environ['PYTHONUNBUFFERED'] = '1'
            
            # 刷新所有输出
            sys.stdout.flush()
            sys.stderr.flush()
            
            # 重要：在转录前，确保 stderr 不被缓冲
            if hasattr(sys.stderr, 'reconfigure'):
                try:
                    sys.stderr.reconfigure(line_buffering=True, encoding='utf-8')
                except Exception:
                    pass
            
            # 临时禁用 Rich 对 stderr 的捕获，让 Whisper 的输出直接显示
            # Whisper 的 verbose 输出会直接打印到 stderr
            try:
                logger.info("="*80)
                logger.info("开始 Whisper 转录流程")
                logger.info("="*80)
                logger.info("初始化 WhisperTranscriber...")
                logger.info(f"音频文件路径: {audio_file}")
                logger.info(f"音频文件存在: {os.path.exists(audio_file)}")
                
                if os.path.exists(audio_file):
                    file_size = os.path.getsize(audio_file)
                    logger.info(f"音频文件大小: {file_size / 1024 / 1024:.2f} MB")
                
                transcriber = WhisperTranscriber()
                logger.info("✓ WhisperTranscriber 初始化完成")
                logger.info("开始调用 transcribe 方法...")
                logger.info("提示：转录可能需要几分钟，请耐心等待...")
                
                # 直接调用，让 Whisper 的 verbose 输出直接显示到终端
                logger.info("调用 transcriber.transcribe()...")
                text_content = transcriber.transcribe(audio_file, cleanup=True)
                logger.info("✓ transcriber.transcribe() 返回成功")
                
                # 确保输出已刷新
                sys.stdout.flush()
                sys.stderr.flush()
                
                logger.info(f"转录结果类型: {type(text_content)}")
                logger.info(f"转录结果长度: {len(text_content) if text_content else 0} 字符")
                
                if not text_content:
                    from .utils.exceptions import TranscriptionError
                    logger.error("转录结果为空！")
                    raise TranscriptionError("转录结果为空")
                
                console.print("")
                console.print(f"[green]✓[/green] 转录完成，文本长度: {len(text_content)} 字符")
                logger.info("="*80)
                logger.info(f"✓ 转录成功，文本长度: {len(text_content)} 字符")
                logger.info("="*80)
            except KeyboardInterrupt:
                console.print("[red]转录被用户中断[/red]")
                logger.warning("转录被用户中断")
                raise click.Abort()
            except SystemExit as e:
                console.print(f"[red]系统退出: {e}[/red]")
                logger.warning(f"系统退出: {e}")
                raise click.Abort()
            except Exception as e:
                # 输出详细错误信息
                import traceback
                error_type = type(e).__name__
                error_msg = str(e)
                console.print(f"[red]转录失败: {error_type}: {error_msg}[/red]")
                console.print(f"[dim]{traceback.format_exc()}[/dim]")
                logger.exception(f"转录失败: {error_type}: {error_msg}")
                # 确保错误信息被输出
                sys.stdout.flush()
                sys.stderr.flush()
                raise click.Abort()
        
        else:
            # 尝试下载字幕
            try:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task("下载字幕文件...", total=None)
                    subtitle_file = platform.download_subtitle(
                        url,
                        use_cache=not no_cache
                    )
                    progress.update(task, completed=True)
                
                console.print(f"[green]✓[/green] 字幕下载完成")
                
                # 提取文本
                extractor = ContentExtractor(platform)
                text_content, _ = extractor.extract(url, subtitle_file)
                console.print(f"[green]✓[/green] 文本提取完成，长度: {len(text_content)} 字符")
            
            except SubtitleNotFoundError:
                # 无字幕，使用 Whisper
                if use_whisper:
                    console.print(f"[bold yellow]视频无字幕，使用 Whisper 转录...[/bold yellow]")
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=console
                    ) as progress:
                        task = progress.add_task("下载音频文件...", total=None)
                        audio_file = platform.download_audio(url)
                        progress.update(task, completed=True)
                    
                    console.print(f"[green]✓[/green] 音频下载完成")
                    
                    console.print("[yellow]提示:[/yellow] Whisper 转录可能需要几分钟，请耐心等待...")
                    console.print("[dim]转录进度会实时显示在下方（实时输出）[/dim]")
                    console.print("")
                    
                    # 确保输出不被缓冲
                    import sys
                    import os
                    os.environ['PYTHONUNBUFFERED'] = '1'
                    
                    # 刷新所有输出
                    sys.stdout.flush()
                    sys.stderr.flush()
                    
                    # 重要：在转录前，确保 stderr 不被缓冲
                    if hasattr(sys.stderr, 'reconfigure'):
                        try:
                            sys.stderr.reconfigure(line_buffering=True, encoding='utf-8')
                        except Exception:
                            pass
                    
                    # 临时禁用 Rich 对 stderr 的捕获，让 Whisper 的输出直接显示
                    # Whisper 的 verbose 输出会直接打印到 stderr
                    try:
                        logger.info("初始化 WhisperTranscriber...")
                        logger.info(f"音频文件路径: {audio_file}")
                        logger.info(f"音频文件存在: {os.path.exists(audio_file) if 'os' in dir() else 'N/A'}")
                        
                        transcriber = WhisperTranscriber()
                        logger.info("WhisperTranscriber 初始化完成")
                        logger.info("开始调用 transcribe 方法...")
                        
                        # 直接调用，让 Whisper 的 verbose 输出直接显示到终端
                        text_content = transcriber.transcribe(audio_file, cleanup=True)
                        
                        # 确保输出已刷新
                        sys.stdout.flush()
                        sys.stderr.flush()
                        
                        if not text_content:
                            raise TranscriptionError("转录结果为空")
                        
                        console.print("")
                        console.print(f"[green]✓[/green] 转录完成，文本长度: {len(text_content)} 字符")
                        logger.info(f"转录成功，文本长度: {len(text_content)} 字符")
                    except KeyboardInterrupt:
                        console.print("[red]转录被用户中断[/red]")
                        logger.warning("转录被用户中断")
                        raise click.Abort()
                    except SystemExit as e:
                        console.print(f"[red]系统退出: {e}[/red]")
                        logger.warning(f"系统退出: {e}")
                        raise click.Abort()
                    except Exception as e:
                        # 输出详细错误信息
                        import traceback
                        error_type = type(e).__name__
                        error_msg = str(e)
                        console.print(f"[red]转录失败: {error_type}: {error_msg}[/red]")
                        console.print(f"[dim]{traceback.format_exc()}[/dim]")
                        logger.exception(f"转录失败: {error_type}: {error_msg}")
                        # 确保错误信息被输出
                        sys.stdout.flush()
                        sys.stderr.flush()
                        raise click.Abort()
                else:
                    raise
        
        if skip_summary:
            output_path = _write_transcript(text_content, metadata, output)
            console.print("[green]✓[/green] 已保存转录文本")
            console.print("")
            console.print(Panel(
                f"[bold green]处理完成！[/bold green]\n\n"
                f"输出文件: [cyan]{output_path}[/cyan]",
                title="成功",
                border_style="green"
            ))
            return str(output_path)

        # AI 总结
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("AI 总结生成中...", total=None)
            summarizer = Summarizer(provider=ai_provider)
            metadata_dict = {
                'title': metadata.title,
                'author': metadata.author,
                'duration': metadata.duration,
            }
            summary = summarizer.summarize(text_content, metadata=metadata_dict)
            progress.update(task, completed=True)
        
        console.print(f"[green]✓[/green] 总结生成完成")
        
        # 生成 Markdown
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("生成 Markdown 文件...", total=None)
            generator = MarkdownGenerator()
            output_path = generator.generate(summary, metadata, filename=output)
            progress.update(task, completed=True)
        
        console.print(f"[green]✓[/green] Markdown 文件已保存")
        
        # 显示结果
        console.print("")
        console.print(Panel(
            f"[bold green]处理完成！[/bold green]\n\n"
            f"输出文件: [cyan]{output_path}[/cyan]",
            title="成功",
            border_style="green"
        ))
        
        return output_path
    
    except PlatformNotSupportedError as e:
        console.print(f"[bold red]错误:[/bold red] {e}")
        raise click.Abort()
    except SubtitleNotFoundError as e:
        console.print(f"[bold red]错误:[/bold red] {e}")
        console.print("[yellow]提示:[/yellow] 使用 --use-whisper 选项可以使用 Whisper 转录无字幕视频")
        raise click.Abort()
    except DownloadError as e:
        console.print(f"[bold red]下载失败:[/bold red] {e}")
        raise click.Abort()
    except TranscriptionError as e:
        console.print(f"[bold red]转录失败:[/bold red] {e}")
        raise click.Abort()
    except AIAPIError as e:
        console.print(f"[bold red]AI API 调用失败:[/bold red] {e}")
        console.print("[yellow]提示:[/yellow] 请检查 API Key 配置")
        raise click.Abort()
    except SmartVideoError as e:
        console.print(f"[bold red]错误:[/bold red] {e}")
        raise click.Abort()
    except Exception as e:
        console.print(f"[bold red]未知错误:[/bold red] {e}")
        logger.exception("处理视频时发生错误")
        raise click.Abort()


@click.command()
@click.option('--url', '-u', required=True, help='视频 URL')
@click.option('--output', '-o', help='输出文件路径（可选）')
@click.option('--ai-provider', '-p', help='AI 提供商（openai）')
@click.option('--use-whisper', is_flag=True, help='无字幕时使用 Whisper 转录')
@click.option('--force-whisper', is_flag=True, help='强制使用 Whisper（即使有字幕）')
@click.option('--no-cache', is_flag=True, help='禁用缓存')
@click.option('--skip-summary', is_flag=True, help='仅生成转录文本，不调用 AI 总结')
def main(url, output, ai_provider, use_whisper, force_whisper, no_cache, skip_summary):
    """
    Smart Video - 智能视频总结工具
    
    支持 YouTube 视频的自动下载、转录和 AI 总结。
    """
    console.print(Panel(
        "[bold cyan]Smart Video[/bold cyan] - 智能视频总结工具",
        border_style="cyan"
    ))
    console.print("")
    
    process_video(
        url=url,
        output=output,
        ai_provider=ai_provider,
        use_whisper=use_whisper,
        force_whisper=force_whisper,
        no_cache=no_cache,
        skip_summary=skip_summary,
    )


if __name__ == '__main__':
    main()
