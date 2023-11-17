import argparse
import sys
import os
import re

def get_mcs_header(sch_lines, mcs_size=0, pcm_data_offset=0, pcm_data_size=0, adpcm_data_offset=0, adpcm_data_size=0, tx_file_offsets=None, tp_file_offsets=None):

  mcs_header = bytearray("MACSDATA".encode("ascii"))
  mcs_header.extend(bytes([0x01, 0x30]))

  mcs_header.extend(mcs_size.to_bytes(4, 'big'))

  for sch in sch_lines:

    while len(sch) > 0 and ord(sch[-1:]) < 0x20:
      sch = sch[:-1]

    re1 = re.match(r"^([^\s]+)\s+'(.+)'\s*", sch.strip())
    re2 = re.match(r'^([^\s]+)\s+"(.+)"\s*', sch.strip())

    if re1:
      sch_args = [ re1.group(1), re1.group(2) ]
    elif re2:
      sch_args = [ re2.group(1), re2.group(2) ]
    else:
      sch_args = sch.strip().split()

    if len(sch_args) == 0:
      continue

    if sch_args[0] == "SET_OFFSET":
      mcs_header.extend(bytes([0x00, 0x01]))

    elif sch_args[0] == "USE_DUALPCM":
      pcm_type = sch_args[1]
      packet = bytearray(("DUALPCM/PCM8PP:"+pcm_type).encode("ascii"))
      if len(packet) % 2 == 1:
        packet.extend(bytes([0x00]))
      else:
        packet.extend(bytes([0x00, 0x00]))
      mcs_header.extend(bytes([0x00, 0x2c, len(packet)//256, len(packet)%256]))
      mcs_header.extend(packet)

    elif sch_args[0] == "TITLE":
      title = sch_args[1]
      packet = bytearray(("TITLE:"+title).encode("cp932"))
      if len(packet) % 2 == 1:
        packet.extend(bytes([0x00]))
      else:
        packet.extend(bytes([0x00, 0x00]))
      mcs_header.extend(bytes([0x00, 0x2c, len(packet)//256, len(packet)%256]))
      mcs_header.extend(packet)

    elif sch_args[0] == "COMMENT":
      comment = sch_args[1]
      packet = bytearray(("COMMENT:"+comment).encode("cp932"))
      if len(packet) % 2 == 1:
        packet.extend(bytes([0x00]))
      else:
        packet.extend(bytes([0x00, 0x00]))
      mcs_header.extend(bytes([0x00, 0x2c, len(packet)//256, len(packet)%256]))
      mcs_header.extend(packet)

    elif sch_args[0] == "SCREEN_ON_G64K":
      mcs_header.extend(bytes([0x00, 0x17]))
    elif sch_args[0] == "SCREEN_ON_G256":
      mcs_header.extend(bytes([0x00, 0x16]))
    elif sch_args[0] == "SCREEN_ON_G384":
      mcs_header.extend(bytes([0x00, 0x29]))

    elif sch_args[0] == "SET_FPS":
      fps = int(sch_args[1])
      mcs_header.extend(bytes([0x00, 0x34]))
      mcs_header.extend(fps.to_bytes(4, 'big'))
    elif sch_args[0] == "SET_FPS":
      fps = int(sch_args[1])
      mcs_header.extend(bytes([0x00, 0x34]))
      mcs_header.extend(fps.to_bytes(4, 'big'))
    elif sch_args[0] == "SET_FPS15":
      fps = 15000
      mcs_header.extend(bytes([0x00, 0x34]))
      mcs_header.extend(fps.to_bytes(4, 'big')) 
    elif sch_args[0] == "SET_FPS15_X68":
      fps = 55458 // 4
      mcs_header.extend(bytes([0x00, 0x34]))
      mcs_header.extend(fps.to_bytes(4, 'big')) 
    elif sch_args[0] == "SET_FPS20_X68":
      fps = 55458 // 3
      mcs_header.extend(bytes([0x00, 0x34]))
      mcs_header.extend(fps.to_bytes(4, 'big')) 
    elif sch_args[0] == "SET_FPS24":
      fps = 24000
      mcs_header.extend(bytes([0x00, 0x34]))
      mcs_header.extend(fps.to_bytes(4, 'big')) 
    elif sch_args[0] == "SET_FPS24_NTSC":
      fps = 23976
      mcs_header.extend(bytes([0x00, 0x34]))
      mcs_header.extend(fps.to_bytes(4, 'big')) 
    elif sch_args[0] == "SET_FPS30":
      fps = 30000
      mcs_header.extend(bytes([0x00, 0x34]))
      mcs_header.extend(fps.to_bytes(4, 'big')) 
    elif sch_args[0] == "SET_FPS30_NTSC":
      fps = 29970
      mcs_header.extend(bytes([0x00, 0x34]))
      mcs_header.extend(fps.to_bytes(4, 'big')) 
    elif sch_args[0] == "SET_FPS30_X68":
      fps = 55458 // 2
      mcs_header.extend(bytes([0x00, 0x34]))
      mcs_header.extend(fps.to_bytes(4, 'big')) 
    elif sch_args[0] == "SET_FPS60_X68":
      fps = 55458
      mcs_header.extend(bytes([0x00, 0x34]))
      mcs_header.extend(fps.to_bytes(4, 'big')) 
    elif sch_args[0] == "SET_FPS_OFF":
      fps = 0
      mcs_header.extend(bytes([0x00, 0x34]))
      mcs_header.extend(fps.to_bytes(4, 'big')) 

    elif sch_args[0] == "SET_VIEWAREA_Y":
      view_height = int(sch_args[1])
      mcs_header.extend(bytes([0x00, 0x38, 0x00, 0x04]))
      mcs_header.extend(view_height.to_bytes(2, 'big'))

    elif sch_args[0] == "PCM_PLAY_S48":
      mcs_header.extend(bytes([0x00, 0x18]))
      mcs_header.extend(pcm_data_offset.to_bytes(4, 'big'))
      mcs_header.extend(pcm_data_size.to_bytes(4, 'big'))
      mcs_header.extend(bytes([0x00, 0x00]))
      mcs_header.extend(bytes([0x00, 0x08, 0x1e, 0x03]))
      mcs_header.extend(bytes([0x00, 0x00, 0x00, 0x00]))

    elif sch_args[0] == "PCM_PLAY_S44":
      mcs_header.extend(bytes([0x00, 0x18]))
      mcs_header.extend(pcm_data_offset.to_bytes(4, 'big'))
      mcs_header.extend(pcm_data_size.to_bytes(4, 'big'))
      mcs_header.extend(bytes([0x00, 0x00]))
      mcs_header.extend(bytes([0x00, 0x08, 0x1d, 0x03]))
      mcs_header.extend(bytes([0x00, 0x00, 0x00, 0x00]))

    elif sch_args[0] == "PCM_PLAY_S32":
      mcs_header.extend(bytes([0x00, 0x18]))
      mcs_header.extend(pcm_data_offset.to_bytes(4, 'big'))
      mcs_header.extend(pcm_data_size.to_bytes(4, 'big'))
      mcs_header.extend(bytes([0x00, 0x00]))
      mcs_header.extend(bytes([0x00, 0x08, 0x1c, 0x03]))
      mcs_header.extend(bytes([0x00, 0x00, 0x00, 0x00]))

    elif sch_args[0] == "PCM_PLAY_S24":
      mcs_header.extend(bytes([0x00, 0x18]))
      mcs_header.extend(pcm_data_offset.to_bytes(4, 'big'))
      mcs_header.extend(pcm_data_size.to_bytes(4, 'big'))
      mcs_header.extend(bytes([0x00, 0x00]))
      mcs_header.extend(bytes([0x00, 0x08, 0x1b, 0x03]))
      mcs_header.extend(bytes([0x00, 0x00, 0x00, 0x00]))

    elif sch_args[0] == "PCM_PLAY_S22":
      mcs_header.extend(bytes([0x00, 0x18]))
      mcs_header.extend(pcm_data_offset.to_bytes(4, 'big'))
      mcs_header.extend(pcm_data_size.to_bytes(4, 'big'))
      mcs_header.extend(bytes([0x00, 0x00]))
      mcs_header.extend(bytes([0x00, 0x08, 0x1a, 0x03]))
      mcs_header.extend(bytes([0x00, 0x00, 0x00, 0x00]))

    elif sch_args[0] == "PCM_PLAY_SUBADPCM":
      mcs_header.extend(bytes([0x00, 0x2d]))
      mcs_header.extend(adpcm_data_offset.to_bytes(4, 'big'))
      mcs_header.extend(adpcm_data_size.to_bytes(4, 'big'))

    elif sch_args[0] == "DRAW_DATA_RP":
      i = int(sch_args[1])
      tx_offset = 0
      tp_offset = 0
      if tx_file_offsets and tp_file_offsets:
        tx_offset = tx_file_offsets[ i - 10000 ]
        tp_offset = tp_file_offsets[ i - 10000 ]
      mcs_header.extend(bytes([0x00, 0x03]))              # DRAW
      mcs_header.extend(tx_offset.to_bytes(4, 'big'))
      mcs_header.extend(bytes([0x00, 0x02, 0x00, 0x02]))  # WAIT 2
      mcs_header.extend(bytes([0x00, 0x07]))              # PALETTE
      mcs_header.extend(tp_offset.to_bytes(4, 'big'))
      mcs_header.extend(bytes([0x00, 0x05]))              # CHANGE_POSITION

    elif sch_args[0] == "DRAW_DATA":
      start_end = sch_args[1].split(",")
      max_frame_index = int(start_end[1])
      for i in range(int(start_end[0]), max_frame_index + 1):
        tx_offset = 0
        tp_offset = 0
        if tx_file_offsets and tp_file_offsets:
          tx_offset = tx_file_offsets[ i - 10000 ]
          tp_offset = tp_file_offsets[ i - 10000 ]
        mcs_header.extend(bytes([0x00, 0x03]))              # DRAW
        mcs_header.extend(tx_offset.to_bytes(4, 'big'))
        mcs_header.extend(bytes([0x00, 0x02, 0x00, 0x02]))  # WAIT 2
        mcs_header.extend(bytes([0x00, 0x07]))              # PALETTE
        mcs_header.extend(tp_offset.to_bytes(4, 'big'))
        mcs_header.extend(bytes([0x00, 0x05]))              # CHANGE_POSITION

    elif sch_args[0] == "WAIT":
      wait_time = int(sch_args[1])
      mcs_header.extend(bytes([0x00, 0x02]))
      mcs_header.extend(wait_time.to_bytes(2, 'big'))

    elif sch_args[0] == "PCM_STOP":
      mcs_header.extend(bytes([0x00, 0x0b]))

    elif sch_args[0] == "EXIT":
      mcs_header.extend(bytes([0x00, 0x00]))

  if len(mcs_header) % 4 != 0:
    mcs_header.extend(bytes([0x00] * (4 - len(mcs_header) % 4)))  

  return (mcs_header, max_frame_index)

def build(sch_file, mcs_file, pcm_file, adpcm_file, lze):

  with open(sch_file, "r", encoding="cp932") as f_sch:


    # pass1 - dummy header construction
    sch_lines = f_sch.readlines()
    mcs_header, max_frame_index = get_mcs_header(sch_lines)


    # pass 2 - offset determination
    current_offset = len(mcs_header) - 14

    pcm_data_offset = current_offset
    pcm_data_size = os.path.getsize(pcm_file)
    current_offset += pcm_data_size
    if pcm_data_size % 4 != 0:
      current_offset += 4 - (pcm_data_size % 4)

    adpcm_data_offset = current_offset
    adpcm_data_size = os.path.getsize(adpcm_file)
    current_offset += adpcm_data_size
    if adpcm_data_size % 4 != 0:
      current_offset += 4 - (adpcm_data_size % 4)

    tx_file_offsets = [0] * (max_frame_index - 10000 + 1)
    tp_file_offsets = [0] * (max_frame_index - 10000 + 1)

    tx_file_sizes = [0] * (max_frame_index - 10000 + 1)
    tp_file_sizes = [0] * (max_frame_index - 10000 + 1)

    for i in range(max_frame_index - 10000 + 1):

      frame_group = i // 500
      frame_index = i + 10000

      if lze:
        tx_file_sizes[i] = os.path.getsize(f"im{frame_group:02d}/Tx{frame_index:05d}.lze")
      else:
        tx_file_sizes[i] = os.path.getsize(f"im{frame_group:02d}/Tx{frame_index:05d}")

      tx_file_offsets[i] = current_offset
      current_offset += tx_file_sizes[i]
      if tx_file_sizes[i] % 4 != 0:
        current_offset += 4 - (tx_file_sizes[i] % 4)

      tp_file_sizes[i] = os.path.getsize(f"im{frame_group:02d}/Tp{frame_index:05d}")
      tp_file_offsets[i] = current_offset
      current_offset += tp_file_sizes[i]
      if tp_file_sizes[i] % 4 != 0:
        current_offset += 4 - (tp_file_sizes[i] % 4)


    # pass 3 - output
    with open(mcs_file, "wb") as f_mcs:

      mcs_size = current_offset + 14

      mcs_header, max_frame_index = get_mcs_header(sch_lines, mcs_size, pcm_data_offset, pcm_data_size, adpcm_data_offset, adpcm_data_size, tx_file_offsets, tp_file_offsets)
      f_mcs.write(mcs_header)
      
      with open(pcm_file, "rb") as f_pcm:
        pcm_data = f_pcm.read()
        f_mcs.write(pcm_data)
        if len(pcm_data) % 4 != 0:
          f_mcs.write(bytes([0] * (4 - len(pcm_data) % 4)))

      with open(adpcm_file, "rb") as f_adpcm:
        adpcm_data = f_adpcm.read()
        f_mcs.write(adpcm_data)
        if len(adpcm_data) % 4 != 0:
          f_mcs.write(bytes([0] * (4 - len(adpcm_data) % 4)))

      for i in range(max_frame_index - 10000 + 1):

        frame_group = i // 500
        frame_index = i + 10000

        if lze:
          tx_file = f"im{frame_group:02d}/Tx{frame_index:05d}.lze"
        else:
          tx_file = f"im{frame_group:02d}/Tx{frame_index:05d}"
        with open(tx_file, "rb") as f_tx:
          tx_data = f_tx.read()
          f_mcs.write(tx_data)
          if len(tx_data) % 4 != 0:
            f_mcs.write(bytes([0] * (4 - len(tx_data) % 4)))

        tp_file = f"im{frame_group:02d}/Tp{frame_index:05d}"
        with open(tp_file, "rb") as f_tp:
          tp_data = f_tp.read()
          f_mcs.write(tp_data)
          if len(tp_data) % 4 != 0:
            f_mcs.write(bytes([0] * (4 - len(tp_data) % 4)))

      print(f"Done - {max_frame_index - 10000 + 1} frames.")

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("sch_file", help="source schedule file (.s)")
    parser.add_argument("mcs_file", help="output mcs file")
    parser.add_argument("-p", "--pcm_file", help="16bit PCM file", default="_wip_pcm.dat")
    parser.add_argument("-a", "--adpcm_file", help="ADPCM file", default="_wip_adpcm.dat")
    parser.add_argument("--lze", help="use LZE compression", action='store_true')

    args = parser.parse_args()

    build(args.sch_file, args.mcs_file, args.pcm_file, args.adpcm_file, args.lze)

if __name__ == "__main__":
    main()
