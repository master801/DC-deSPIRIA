#!/usr/bin/env python3
# Created by Master on 4/24/2023 at 5:04 AM CDT

import argparse
import os
import io
import struct
import glob

MAGIC: bytes = b'SC01'


def dump_text(root_dir: str, fn: str, output_dir: str):
    fp = os.path.join(root_dir, fn)

    print(f'Reading \".EVT\" file \"{fp}\"...')
    dumped: list = []
    with open(fp, mode='rb+') as io_evt:
        if io_evt.read(0x04) != MAGIC:
            print('Not an \"EVT\" script file!')
            return
        else:
            print('Passed magic')
            pass
        eof: int = io_evt.seek(0, io.SEEK_END)

        io_evt.seek(0x14, io.SEEK_SET)  # 0x14 is text section pointer
        text_start_address = struct.unpack('<I', io_evt.read(0x04))[0]

        io_evt.seek(text_start_address, io.SEEK_SET)
        while io_evt.tell() != eof:  # text section is last block of file
            buf: bytearray = bytearray()
            while io_evt.tell() != eof:  # better solution than while True loop
                if io_evt.read(0x02) == b'\x00\x00':
                    io_evt.seek(-4, io.SEEK_CUR)  # TODO Check if control code is 4 bytes
                    if io_evt.read(0x02) == b'\xFF\x01':  # only FF 01 has this problem :shrug:
                        buf += io_evt.read(0x02)  # 00 00
                        pass
                    else:
                        io_evt.seek(2, io.SEEK_CUR)
                        break
                    pass
                else:
                    io_evt.seek(-2, io.SEEK_CUR)
                    buf += io_evt.read(0x02)
                    pass
                continue
            buf: bytes = bytes(buf)  # make read-only

            print(f'Found line at 0x{io_evt.tell() - len(buf) - 2:06X}')

            write_buffer: bytearray = bytearray(buf)
            while b'\xFF' in write_buffer:
                i = write_buffer.index(0xFF)
                control_code_build = []
                eat = 1
                if write_buffer[i+1] == 0x00:  # FF 00
                    control_code_build.append('NEWLINE')
                    eat += 1
                    pass
                elif write_buffer[i+1] == 0x01:  # FF 01 XX XX
                    control_code_build.append('RAW')  # TODO
                    control_code_build.append('01')
                    eat += 1

                    control_code_build.append(f'{write_buffer[i+2]:02X}')
                    control_code_build.append(f'{write_buffer[i+3]:02X}')
                    eat += 2
                    pass
                elif write_buffer[i+1] == 0x02:  # FF 02 0F 0F 00 0F - FF 02 XX XX XX XX XX (?)
                    control_code_build.append('RAW')  # TODO
                    control_code_build.append('02')
                    eat += 1
                    # 0F 0F 00 0F - Colors as yellow?!
                    control_code_build.append(f'{write_buffer[i+2]:02X}')
                    control_code_build.append(f'{write_buffer[i+3]:02X}')
                    control_code_build.append(f'{write_buffer[i+4]:02X}')
                    control_code_build.append(f'{write_buffer[i+5]:02X}')
                    eat += 4
                    pass
                elif write_buffer[i+1] == 0x04:  # FF 04
                    control_code_build.append('RAW')  # TODO
                    control_code_build.append('04')
                    eat += 1
                    pass
                elif write_buffer[i+1] == 0x12:  # FF 12
                    control_code_build.append('PAUSE')
                    eat += 1
                    pass
                elif write_buffer[i+1] == 0x14:  # FF 14 XX XX
                    # TODO
                    # FF 14 97 20 - This ALSO colors it green?!
                    control_code_build.append('RAW')
                    control_code_build.append('14')
                    eat += 1
                    control_code_build.append(f'{write_buffer[i+2]:02X}')
                    control_code_build.append(f'{write_buffer[i+3]:02X}')
                    eat += 2
                    pass
                elif write_buffer[i+1] == 0x15:  # FF 15 XX XX
                    control_code_build.append('COLOR')
                    eat += 1

                    if write_buffer[i+2] == 0x01:  # TODO
                        control_code_build.append(f'{write_buffer[i+2]:02X}')
                        pass
                    elif write_buffer[i+2] == 0x11:  # green
                        control_code_build.append('GREEN')
                        pass
                    elif write_buffer[i+2] == 0x21:  # TODO
                        control_code_build.append(f'{write_buffer[i+2]:02X}')
                        pass
                    elif write_buffer[i+2] == 0x31:  # TODO
                        # Also green?!
                        control_code_build.append(f'{write_buffer[i+2]:02X}')
                        pass
                    elif write_buffer[i+2] == 0x41:  # TODO
                        control_code_build.append(f'{write_buffer[i+2]:02X}')
                        pass
                    elif write_buffer[i+2] == 0x51:  # TODO
                        # Also green?!
                        control_code_build.append(f'{write_buffer[i+2]:02X}')
                        pass
                    elif write_buffer[i+2] == 0x61:  # TODO
                        control_code_build.append(f'{write_buffer[i+2]:02X}')
                        pass
                    elif write_buffer[i+2] == 0x71:  # TODO
                        # Also green?!
                        control_code_build.append(f'{write_buffer[i+2]:02X}')
                        pass
                    elif write_buffer[i+2] == 0x81:  # TODO
                        control_code_build.append(f'{write_buffer[i+2]:02X}')
                        pass
                    elif write_buffer[i+2] == 0x91:  # TODO
                        # Also green?!
                        control_code_build.append(f'{write_buffer[i+2]:02X}')
                        pass
                    else:
                        print(hex(write_buffer[i+2]))
                        raise SystemError()
                        pass
                    eat += 1

                    if write_buffer[i+3] == 0x00:  # TODO
                        control_code_build.append(f'{write_buffer[i+3]:02X}')
                        pass
                    elif write_buffer[i+3] == 0x01:  # TODO
                        control_code_build.append(f'{write_buffer[i+3]:02X}')
                        pass
                    elif write_buffer[i+3] == 0x02:  # TODO
                        control_code_build.append(f'{write_buffer[i+3]:02X}')
                        pass
                    elif write_buffer[i+3] == 0x03:  # TODO
                        control_code_build.append(f'{write_buffer[i+3]:02X}')
                        pass
                    elif write_buffer[i+3] == 0x04:  # TODO
                        control_code_build.append(f'{write_buffer[i+3]:02X}')
                        pass
                    elif write_buffer[i+3] == 0x05:  # TODO
                        control_code_build.append(f'{write_buffer[i+3]:02X}')
                        pass
                    elif write_buffer[i+3] == 0x06:  # TODO
                        control_code_build.append(f'{write_buffer[i+3]:02X}')
                        pass
                    else:
                        print(f'{write_buffer[i+3]}')
                        raise SystemError()
                        pass
                    eat += 1
                    pass
                elif write_buffer[i+1] == 0x16:  # FF 16
                    eat += 1
                    control_code_build.append('UNCOLOR')  # TODO Is this truly uncolor? Or reset?
                    pass
                else:
                    raise NotImplementedError(f'Unsupported control code \"0x{write_buffer[i + 1]:02X}\"!')

                built = '<' + ' '.join(control_code_build) + '>'
                write_buffer[i:i+eat] = built.encode(encoding='ascii')

                del built
                del eat
                del control_code_build
                del i
                continue

            decoded = write_buffer.decode(encoding='shift-jis')
            dumped.append(decoded)

            print(f'Decoded line as \"{decoded}\"\n')

            del write_buffer
            continue
        pass

    fp_dumped = os.path.join(output_dir, fn + '.TXT')
    if os.path.exists(fp_dumped):
        dumped_mode = 'w+'
        pass
    else:
        dumped_mode = 'x'
        pass

    print(f'Writing text file \"{fp_dumped}\"...')
    with open(fp_dumped, mode=f'{dumped_mode}t', encoding='utf-8', newline='\n') as io_dumped:
        for i in dumped:
            io_dumped.write(i)
            io_dumped.write('\n')
            continue
        pass
    print('Done!\n\n')
    return


def dump(_input: str, output_dir: str):
    for i in glob.glob('*.EVT', root_dir=_input, recursive=False):
        dump_text('EVT', i, output_dir)
        continue
    return


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--dump', action='store_true')
    argparser.add_argument('--input', required=True, type=str)
    argparser.add_argument('--output', required=True, type=str)
    args = argparser.parse_args()
    if args.dump:
        dump(args.input, args.output)
        pass
    else:
        print('No action specified!')
        pass
    return


if __name__ == '__main__':
    main()
    pass
