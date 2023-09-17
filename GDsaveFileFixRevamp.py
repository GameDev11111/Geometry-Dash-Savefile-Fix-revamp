# -*- coding: utf-8 -*-
import base64
import datetime
import os
import shutil
import struct
import sys
import traceback
import zlib
from textwrap import dedent
from pathlib import Path

__version__ = '0.1 ALPHA'

SAVEFILE_NAME = ['CCGameManager.dat', 'CCLocalLevels.dat', 'CCGameManager2.dat', 'CCLocalLevels2.dat']
SAVEFILE_PATH = Path(os.getenv('LocalAppData')) / 'GeometryDash'

print("This fork is very early in development, so bugs may come up. One were trying to fix is not being able tto backup save files. At this moment, please back them up manualy")

def main():
    print(dedent(
        f"""\
        Geometry Dash Savefile Fix v{__version__} by WEGFan- revamp by Skidder100
        This tool can fix most problems caused unable to open the game by the savefiles.
        (which is the game will only launch if you move the savefiles to other folders)

        If you encounter any problem (unable to fix / doesn't work after fixed),
        feel free to create an issue or contact me on Discord (amw_).
        """
    ))

    print(f'Savefiles location: {SAVEFILE_PATH}')
    print()

    os.chdir(SAVEFILE_PATH)

    # backup original file
    backup_folder_name = f"backup_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    os.mkdir(backup_folder_name)
    for savefile in SAVEFILE_NAME:
        try:
            shutil.copyfile(savefile, Path(backup_folder_name, savefile))
        except Exception as err:
            print(f'Failed to backup {savefile}! This *may* have deleted a few levels in your created levels folder!')
    print(f'Savefiles backed up to {SAVEFILE_PATH / backup_folder_name}')
    print()

    input('Press ENTER to fix...')
    print()

    for savefile in SAVEFILE_NAME:
        try:
            with open(savefile, 'rb') as f:
                savedata = f.read()

            print(f'Fixing {savefile}...')

            # decrypt
            decrypted_data = bytes(i ^ 11 for i in savedata)
            decoded_data = base64.b64decode(decrypted_data, altchars='-_')
            decompressed_data = zlib.decompress(decoded_data[10:], -zlib.MAX_WBITS)

            # fix (i don't know why simply add spaces works...)
            decompressed_data = decompressed_data.replace(b'><', b'> <', 50)

            # encrypt
            compressed_data = zlib.compress(decompressed_data)
            data_crc32 = zlib.crc32(decompressed_data)
            data_size = len(decompressed_data)

            compressed_data = (b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\x0b' +  # gzip header
                               compressed_data[2:-4] +
                               struct.pack('I I', data_crc32, data_size))

            encoded_data = base64.b64encode(compressed_data, altchars=b'-_')
            encrypted_data = bytes(i ^ 11 for i in encoded_data)

            with open(savefile, 'wb') as f:
                f.write(encrypted_data)

            print(f'{savefile} fixed!')
        except FileNotFoundError as err:
            print(f"Can't find {savefile}!")
        except Exception as err:
            print(f'There is an issue fixing {savefile}!')
            traceback.print_exc()

    print()
    input('Done! Press ENTER to exit...')


if __name__ == '__main__':
    try:
        main()
    except (EOFError, KeyboardInterrupt) as err:
        sys.exit()
    except Exception as err:
        print('Oops, something went wrong...')
        print('Error message:')
        traceback.print_exc()
