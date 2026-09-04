import asyncio


async def handle(reader, writer):
    async def send(line):
        writer.write((line + "\r\n").encode())
        await writer.drain()

    await send("220 sink ESMTP")
    data_mode = False
    buf = []
    try:
        while True:
            raw = await reader.readline()
            if not raw:
                break
            line = raw.decode(errors="replace").rstrip("\r\n")
            if data_mode:
                if line == ".":
                    data_mode = False
                    print("MAIL", "\n".join(buf)[:300], flush=True)
                    buf = []
                    await send("250 OK")
                else:
                    buf.append(line)
                continue
            cmd = line.split(" ", 1)[0].upper()
            if cmd == "EHLO" or cmd == "HELO":
                await send("250-sink")
                await send("250-AUTH LOGIN PLAIN")
                await send("250 OK")
            elif cmd == "AUTH":
                await send("235 2.7.0 Authentication successful")
            elif cmd == "DATA":
                data_mode = True
                await send("354 End data with <CR><LF>.<CR><LF>")
            elif cmd == "QUIT":
                await send("221 Bye")
                break
            else:
                await send("250 OK")
    finally:
        writer.close()
        await writer.wait_closed()


async def main():
    server = await asyncio.start_server(handle, "0.0.0.0", 1025)
    print("smtp sink ready on :1025", flush=True)
    async with server:
        await server.serve_forever()


asyncio.run(main())
