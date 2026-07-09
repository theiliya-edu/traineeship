import asyncio
import datetime

from spimex_parser.pipeline.usecase import DownloadContentSinceDateUseCase


async def main() -> None:
    usecase = DownloadContentSinceDateUseCase(
        datetime.datetime.strptime("20260601", "%Y%m%d").date(),
    )

    await usecase.execute()


if __name__ == "__main__":
    asyncio.run(main())
