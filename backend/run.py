import argparse
import asyncio
import sys
from pathlib import Path


if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

sys.path.insert(0, str(Path(__file__).resolve().parent))

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8081)
    parser.add_argument('--reload', action='store_true')
    args = parser.parse_args()

    uvicorn.run(
        'app.main:app',
        host=args.host,
        port=args.port,
        reload=args.reload,
        reload_dirs=[str(Path(__file__).resolve().parent)] if args.reload else None,
        loop='asyncio',
    )


if __name__ == '__main__':
    main()
