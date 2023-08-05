#!/usr/bin/env python

"""Unittest for kegboard module"""

import os
import unittest
import struct

from kegbot.kegboard import kegboard

TESTDATA_PATH = os.path.join(os.path.dirname(kegboard.__file__), 'testdata')
CAP_FILE = os.path.join(TESTDATA_PATH, 'one_flow_active.bin')


class MessageTestCase(unittest.TestCase):
  def testMessageCreate(self):
    hello_bytes = kegboard.KBSP_PREFIX + '\x01\x00\x04\x00\x01\x02\x03\x00\x3f\x29\r\n'
    m = kegboard.HelloMessage(bytes=hello_bytes)
    self.assertEqual(m.firmware_version, 3)

    m = kegboard.get_message_for_bytes(hello_bytes)
    self.assertEqual(m.firmware_version, 3)
    print m


class KegboardReaderTestCase(unittest.TestCase):
  def testBasicUse(self):
    kbr = kegboard.Kegboard(CAP_FILE)

    kbr.open()
    try:
      # read the first 8 messages
      messages = []
      for i in xrange(8):
        messages.append(kbr.read_message_nonblock())
      print 'messages:'
      print '\n'.join('  %s' % msg for msg in messages)

      hello_message = kegboard.HelloMessage()
      hello_message.SetValue('firmware_version', 3)
      self.assertEqual(messages[0], hello_message)

      onewire_message = kegboard.OnewirePresenceMessage()
      onewire_message.SetValue('device_id', 0)
      self.assertEqual(messages[1], onewire_message)

      message_bytes = messages[2].ToBytes()
      new_message = kegboard.get_message_for_bytes(message_bytes)
      self.assertEqual(message_bytes, new_message.ToBytes())
    finally:
      kbr.close_quietly()

  def testAgainstBogusData(self):
    pass

if __name__ == '__main__':
  import logging
  logging.basicConfig()
  unittest.main()
