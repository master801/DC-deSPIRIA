#!/usr/bin/env python3
# Created by Master on 4/24/2023 at 5:04 AM CDT

import argparse
import os
import io
import struct
import glob
import csv

MAGIC: bytes = b'SC01'


def insert_text(csv_file: str, evt_file: str, out_dir: str):
    print(f'Reading CSV \"{csv_file}\"...')
    csv_lines: list = []
    with open(csv_file, mode='rt+', encoding='utf-8', newline='') as io_csv:
        reader = csv.reader(io_csv, quotechar='\"', quoting=csv.QUOTE_NONNUMERIC)
        for line in reader:
            csv_lines.append(line)
            continue
        del line
        csv_lines.pop(0)  # pop first entry - header
        del reader  # we don't need the csv reader anymore
        pass
    print(f'Read {len(csv_lines)-1} lines')
    print('Done reading CSV file')

    with open(evt_file, mode='rb+') as io_evt:
        if io_evt.read(0x04) != MAGIC:
            print(f'File \"{evt_file}\" is not an \"EVT\" script file!')
            return
        else:
            print('Passed magic')

            io_evt.seek(0, io.SEEK_SET)  # reset
            bytes_evt = io.BytesIO(io_evt.read())
            pass
        pass
    del io_evt

    eof: int = bytes_evt.seek(0x00, io.SEEK_END)

    bytes_evt.seek(0x14, io.SEEK_SET)  # 0x14 is text section pointer
    text_start_address = struct.unpack('<I', bytes_evt.read(0x04))[0]

    bytes_evt.seek(text_start_address, io.SEEK_SET)

    for i in range(len(csv_lines)):
        csv_line: list[str, str] = csv_lines[i]
        if len(csv_line[1]) == 0:  # No Eng, use Jap
            line = csv_line[0].encode(encoding='shift-jis')
            pass
        else:  # Eng
            line = csv_line[1].encode(encoding='shift-jis')  # TODO Use other encoding
            pass

        write_buffer: bytearray = bytearray(line)
        while b'<' in write_buffer:
            i = write_buffer.index(b'<')
            j = write_buffer.index(b'>')
            control_codes = write_buffer[i+1:j].decode(encoding='ascii').split(' ')

            build: bytearray = bytearray()
            if control_codes[0] == 'NEWLINE':
                build += b'\xFF\x00'
                pass
            elif control_codes[0] == 'PAUSE':
                build += b'\xFF\x12'
                pass
            elif control_codes[0] == 'COLOR':
                build += b'\xFF\x15'
                if control_codes[1] == '01':  # 0x01
                    build += b'\x01'
                    pass
                elif control_codes[1] == 'GREEN':  # 0x11
                    build += b'\x11'
                    pass
                elif control_codes[1] == '21':  # 0x21
                    build += b'\x21'
                    pass
                elif control_codes[1] == '31':  # 0x31
                    build += b'\x31'
                    pass
                elif control_codes[1] == '41':  # 0x41
                    build += b'\x41'
                    pass
                elif control_codes[1] == '51':  # 0x51
                    build += b'\x51'
                    pass
                elif control_codes[1] == '61':  # 0x61
                    build += b'\x61'
                    pass
                elif control_codes[1] == '71':  # 0x71
                    build += b'\x71'
                    pass
                elif control_codes[1] == '81':  # 0x81
                    build += b'\x81'
                    pass
                elif control_codes[1] == '91':  # 0x91
                    build += b'\x91'
                    pass
                else:
                    raise NotImplementedError()

                if control_codes[2] == '00':  # 0x00
                    build += b'\x00'
                    pass
                elif control_codes[2] == '01':  # 0x01
                    build += b'\x01'
                    pass
                elif control_codes[2] == '02':  # 0x02
                    build += b'\x02'
                    pass
                elif control_codes[2] == '03':  # 0x03
                    build += b'\x03'
                    pass
                elif control_codes[2] == '04':  # 0x04
                    build += b'\x04'
                    pass
                elif control_codes[2] == '05':  # 0x05
                    build += b'\x05'
                    pass
                elif control_codes[2] == '06':  # 0x06
                    build += b'\x06'
                    pass
                else:
                    raise NotImplementedError()
                pass
            elif control_codes[0] == 'UNCOLOR':
                build += b'\xFF\x16'
                pass
            elif control_codes[0] == 'RAW':
                if control_codes[1] == '01':
                    build += b'\xFF\x01'
                    build += bytearray.fromhex(control_codes[2])
                    build += bytearray.fromhex(control_codes[3])
                    pass
                elif control_codes[1] == '02':
                    build += b'\xFF\x02'
                    build += bytearray.fromhex(control_codes[2])
                    build += bytearray.fromhex(control_codes[3])
                    build += bytearray.fromhex(control_codes[4])
                    build += bytearray.fromhex(control_codes[5])
                    pass
                elif control_codes[1] == '04':
                    build += b'\xFF\x04'
                    pass
                elif control_codes[1] == '14':
                    build += b'\xFF\x14'
                    build += bytearray.fromhex(control_codes[2])
                    build += bytearray.fromhex(control_codes[3])
                    pass
                else:
                    raise NotImplementedError()
                pass
            else:
                raise NotImplementedError()
            write_buffer[i:j+1] = build
            continue

        bytes_evt.write(write_buffer)
        bytes_evt.write(b'\x00\x00')
        continue

    # while bytes_evt.tell() != eof:
    #     bytes_evt.write(b'\x00')  # zero everything out after writing modified text lines
    #     continue

    if os.path.sep in evt_file:
        fn = evt_file[evt_file.rindex(os.path.sep)+1:]
        pass
    else:
        fn = evt_file
        pass
    fp = os.path.join(out_dir, fn)
    if os.path.exists(fp):
        mode_evt = 'w+'
        pass
    else:
        mode_evt = 'x'
        pass
    with open(fp, mode=f'{mode_evt}b') as io_evt:
        bytes_evt.seek(0x00, io.SEEK_SET)
        io_evt.write(
            bytes_evt.read()
        )
        pass
    del io_evt
    return


def insert(csv_dir: str, evt_dir: str, out_dir: str):
    evt_files: list[str] = []
    for i in glob.glob1(evt_dir, '*.EVT'):
        evt_files.append(os.path.join(evt_dir, i))
        continue

    csv_files: list[str] = []
    for i in glob.glob1(csv_dir, '*.EVT.CSV'):
        csv_files.append(os.path.join(csv_dir, i))
        continue

    if len(evt_files) != len(csv_files):
        print('Inconsistent list for EVT and CSV!')
        print(f'EVT: {len(evt_files)}, CSV: {len(csv_files)}')
        return

    for i in range(len(evt_files)):
        print(f'Inserting text into EVT file \"{evt_files[i]}\"...')
        insert_text(csv_files[i], evt_files[i], out_dir)
        print(f'Done inserting text into EVT file\n')
        continue
    return


def dump_text(root_dir: str, fn: str, output_dir: str):
    fp = os.path.join(root_dir, fn)

    print(f'Reading \".EVT\" file \"{fp}\"...')
    dumped: list = []
    with open(fp, mode='rb+') as io_evt:
        if io_evt.read(0x04) != MAGIC:
            print(f'File \"{fp}\" is not an \"EVT\" script file!')
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

            print(f'Found line at 0x{(io_evt.tell() - len(buf) - 2):06X}')

            write_buffer: bytearray = bytearray(buf)
            while b'\xFF' in write_buffer:
                i = write_buffer.index(0xFF)
                eat = 1
                control_code_build = []
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
                del control_code_build
                del eat
                del i
                continue

            decoded = write_buffer.decode(encoding='shift-jis')
            dumped.append(decoded)

            print(f'Decoded line as \"{decoded}\"\n')

            del write_buffer
            del buf
            continue

        del eof
        pass

    fp_dumped = os.path.join(output_dir, fn + '.CSV')
    if os.path.exists(fp_dumped):
        dumped_mode = 'w+'
        pass
    else:
        dumped_mode = 'x'
        pass

    print(f'Writing text file \"{fp_dumped}\"...')
    with open(fp_dumped, mode=f'{dumped_mode}t', encoding='utf-8', newline='') as io_dumped:
        writer = csv.writer(io_dumped, quotechar='\"', quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(['jap', 'eng'])
        for i in dumped:
            writer.writerow([i, ''])
            continue
        pass
    print('Done!\n\n')

    del dumped_mode
    del fp_dumped
    return


def dump(_input: str, output_dir: str):
    for i in glob.glob('*.EVT', root_dir=_input, recursive=False):
        dump_text(_input, i, output_dir)
        continue
    return


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--dump', action='store_true')
    arg_parser.add_argument('--insert', action='store_true')
    arg_parser.add_argument('--evt', required=True, type=str)
    arg_parser.add_argument('--csv', required=True, type=str)
    arg_parser.add_argument('--out', required=False, type=str)
    args = arg_parser.parse_args()
    if args.dump and args.insert:
        print('Cannot dump and insert at the same time!')
        return
    elif args.dump:
        dump(args.evt, args.csv)
        pass
    elif args.insert:
        if args.out:
            insert(args.csv, args.evt, args.out)
            pass
        else:
            print('No output specified!')
            return
        pass
    else:
        print('No action specified!')
        pass
    return


if __name__ == '__main__':
    main()
    pass
