#!/usr/bin/env python3

import os
import asyncio
import argparse
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

load_dotenv()


async def run():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Interact with Shapes API')
    parser.add_argument('message', nargs='*', help='Message to send to the shape')
    parser.add_argument('--user-id', help='User ID for the request')
    parser.add_argument('--channel-id', help='Channel ID for the request')

    args = parser.parse_args()

    # If the user provided a message on the command line, use that one
    if args.message:
        messages = [
            {
                "role": "user",
                "content": " ".join(args.message),
            }
        ]
    else:
        # Depending on the shape personality and the history, this messge might trigger various reactions
        messages = [
            {
                "role": "user",
                "content": "Hello. What's your name?",
            }
        ]

    try:
        shape_api_key = os.getenv("SHAPESINC_API_KEY")
        shape_username = os.getenv("SHAPESINC_SHAPE_USERNAME")

        # Check for SHAPESINC_API_KEY in .env
        if not shape_api_key:
            raise ValueError("SHAPESINC_API_KEY not found in .env")

        # Check for SHAPESINC_SHAPE_USERNAME in .env
        if not shape_username:
            raise ValueError("SHAPESINC_SHAPE_USERNAME not found in .env")

        # Create the client with the shape API key and the Shapes API base URL
        aclient_shape = AsyncOpenAI(
            api_key=shape_api_key,
            base_url="https://api.shapes.inc/v1/",
        )

        # Set up headers for user identification and conversation context
        headers = {}
        if args.user_id:
            headers["X-User-Id"] = args.user_id  # If not provided, all requests will be attributed to
            # the user who owns the API key. This will cause unexpected behavior if you are using the same API
            # key for multiple users. For production use cases, either provide this header or obtain a
            # user-specific API key for each user.
        
        # Only add channel ID if provided
        if args.channel_id:
            headers["X-Channel-Id"] = args.channel_id  # If not provided, all requests will be attributed to
            # the user. This will cause unexpected behavior if interacting with multiple users
            # in a group.

        # Send the message to the shape. This will use the shape configured model.
        # WARNING: If the shape is premium, this will also consume credits.
        resp: ChatCompletion = await aclient_shape.chat.completions.create(
            model=f"shapesinc/{shape_username}",
            messages=messages,
            extra_headers=headers,
        )
        print(f"Raw response: {resp}\n")

        if resp.choices and len(resp.choices) > 0:
            final_response = resp.choices[0].message.content
            print(f"Reply: {final_response}")
        else:
            print(f"No choices in response: {resp}")

    except Exception as e:
        print(f"Error: {e}")


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
