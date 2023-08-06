
#line 1 "build/packet_actions.rl"
#ifdef ARDUINO
#include <Arduino.h>
#endif  // #ifdef ARDUINO


#line 190 "build/packet_actions.rl"


#include <stdio.h>
#include <string.h>
#include "PacketParser.h"


#line 17 "build/packet_actions.cpp"
static const int packet_grammar_start = 10;
static const int packet_grammar_first_final = 10;
static const int packet_grammar_error = 0;

static const int packet_grammar_en_process_payload = 11;
static const int packet_grammar_en_main = 10;


#line 197 "build/packet_actions.rl"

template <typename Packet>
inline void PacketParser<Packet>::reset() {
  /*
   * Attempt to parse a packet from a buffer with length `buffer_len`.
   *
   * If successful, return `true` and set:
   *
   *  - `packet.type_`
   *  - `packet.payload_buffer_`
   *  - `packet.payload_length_`
   *
   * __NB__ No data is copied from the input `buffer` to
   * `packet.payload_buffer_`.  Instead, `packet.payload_buffer_` is set to
   * the location in `bufffer` where the payload is found during parsing,
   * while `packet.payload_length_` is set to the length of the
   * payload.  This means that the pointer `packet.payload_buffer_` is only
   * valid as long as `buffer` is valid.
   *
   * If unsuccessful, return `false`.  In the case of an unsuccessful parse
   * attempt, the state of attributes the attributes of `packet` are
   * _undefined_.
   */
  packet_->reset();
  crc_ = 0;
  message_completed_ = false;
  parse_error_ = false;

  
#line 56 "build/packet_actions.cpp"
	{
	cs = packet_grammar_start;
	top = 0;
	}

#line 226 "build/packet_actions.rl"
}


template <typename Packet>
inline void PacketParser<Packet>::parse_byte(uint8_t *byte) {
  uint8_t dummy_byte;

  if (byte == NULL) {
    /* If no byte is available _(i.e., `NULL` byte pointer was provided)_, set
     * Ragel parser pointers to trigger end-of-file actions. */
    p = &dummy_byte;
    pe = p;
    eof = p;
  } else {
    p = byte;
    pe = p + 1;
  }

  
#line 82 "build/packet_actions.cpp"
	{
	if ( p == pe )
		goto _test_eof;
	goto _resume;

_again:
	switch ( cs ) {
		case 10: goto st10;
		case 0: goto st0;
		case 1: goto st1;
		case 2: goto st2;
		case 3: goto st3;
		case 4: goto st4;
		case 5: goto st5;
		case 6: goto st6;
		case 7: goto st7;
		case 8: goto st8;
		case 9: goto st9;
		case 11: goto st11;
		case 12: goto st12;
	default: break;
	}

	if ( ++p == pe )
		goto _test_eof;
_resume:
	switch ( cs )
	{
tr5:
#line 50 "build/packet_actions.rl"
	{
#ifdef VERBOSE_STATES
  std::cout << "[type_received]: " << static_cast<int>(*p) << std::endl;
#endif  // #ifdef VERBOSE_STATES
  packet_->type(*p);
}
#line 166 "build/packet_actions.rl"
	{
#ifdef VERBOSE_STATES
  std::cout << "[ack_received]" << std::endl;
#endif  // #ifdef VERBOSE_STATES
  message_completed_ = true;
}
	goto st10;
tr10:
#line 132 "build/packet_actions.rl"
	{
#ifdef VERBOSE_STATES
  std::cout << "[crc_byte_received]: " << std::hex << static_cast<int>(0x00FFFF & *p) << std::endl;
#endif  // #ifdef VERBOSE_STATES
  packet_->crc_ <<= 8;
  packet_->crc_ += *p;
}
#line 140 "build/packet_actions.rl"
	{
#ifdef VERBOSE_STATES
  std::cout << "[crc_received]: "
            << "from packet: " << packet_->crc_ << ", computed: " << crc_
            << std::endl;
#endif  // #ifdef VERBOSE_STATES
  if (packet_->crc_ == crc_) {
    /* The CRC checksum computed based on payload contents matches the CRC
     * checksum included from the packet.  We assume the packet was
     * successfully received.
     *
     * TODO
     * ====
     *
     * The CRC checksum should be computed from _all bytes in the packet_, not
     * just the _payload_.  This will help to ensure that the identifier, type,
     * etc. are not corrupted during transmission. */
    message_completed_ = true;
    /* Update payload length, since we successfully parsed the packet. */
    packet_->payload_length_ = payload_bytes_received_;
  } else {
    /* Reset state of packet, since the parsing was not successful. */
    parse_error_ = true;
  }
}
	goto st10;
tr11:
#line 57 "build/packet_actions.rl"
	{
#ifdef VERBOSE_STATES
  std::cout << "[length_received]: " << static_cast<int>(*p) << std::endl;
#endif  // #ifdef VERBOSE_STATES
#ifdef ARDUINO_DEBUG
  Serial.print("[len]: ");
  Serial.print(static_cast<int>(*p));
  Serial.print("/");
  Serial.println(packet_->buffer_size_);
#endif  // #ifdef ARDUINO_DEBUG
  payload_bytes_expected_ = *p;
  if (payload_bytes_expected_ > packet_->buffer_size_) {
#ifndef AVR
      std::cerr << "[ERROR]: expected length is too long for buffer.  "
                   "Buffer length is " << packet_->buffer_size_ << std::endl;
#endif  // #ifndef AVR
    parse_error_ = true;
  }
}
#line 173 "build/packet_actions.rl"
	{
#ifdef VERBOSE_STATES
  std::cout << "[nack_received]" << std::endl;
#endif  // #ifdef VERBOSE_STATES
  message_completed_ = true;
  packet_->payload_length_ = payload_bytes_expected_;
}
	goto st10;
st10:
	if ( ++p == pe )
		goto _test_eof10;
case 10:
#line 197 "build/packet_actions.cpp"
	if ( (*p) == 124u )
		goto st1;
	goto st0;
st0:
cs = 0;
	goto _out;
st1:
	if ( ++p == pe )
		goto _test_eof1;
case 1:
	if ( (*p) == 124u )
		goto st2;
	goto st0;
st2:
	if ( ++p == pe )
		goto _test_eof2;
case 2:
	if ( (*p) == 124u )
		goto tr2;
	goto st0;
tr2:
#line 22 "build/packet_actions.rl"
	{
#ifdef VERBOSE_STATES
  std::cout << "[startflag_received]" << std::endl;
#endif  // #ifdef VERBOSE_STATES
#ifdef ARDUINO_DEBUG
  Serial.println("[startflag_received]");
#endif  // #ifdef ARDUINO_DEBUG
  // We're starting to process a new packet, so reset completed status.
  message_completed_ = false;
}
	goto st3;
st3:
	if ( ++p == pe )
		goto _test_eof3;
case 3:
#line 235 "build/packet_actions.cpp"
	goto tr3;
tr3:
#line 33 "build/packet_actions.rl"
	{
#ifdef VERBOSE_STATES
  std::cout << "[id_start]" << std::endl;
#endif  // #ifdef VERBOSE_STATES
  /* Reset the interface unique packet identifier. */
  packet_->iuid_ = 0;
}
#line 41 "build/packet_actions.rl"
	{
#ifdef VERBOSE_STATES
  std::cout << "[id_octet_received]" << std::endl;
#endif  // #ifdef VERBOSE_STATES
  /* Shift previous contents of interface unique packet identifier 8-bits to
   * the left, and write incoming byte as next byte of identifier. */
  packet_->iuid_ = (packet_->iuid_ << 8) | *p;
}
	goto st4;
st4:
	if ( ++p == pe )
		goto _test_eof4;
case 4:
#line 260 "build/packet_actions.cpp"
	goto tr4;
tr4:
#line 41 "build/packet_actions.rl"
	{
#ifdef VERBOSE_STATES
  std::cout << "[id_octet_received]" << std::endl;
#endif  // #ifdef VERBOSE_STATES
  /* Shift previous contents of interface unique packet identifier 8-bits to
   * the left, and write incoming byte as next byte of identifier. */
  packet_->iuid_ = (packet_->iuid_ << 8) | *p;
}
	goto st5;
st5:
	if ( ++p == pe )
		goto _test_eof5;
case 5:
#line 277 "build/packet_actions.cpp"
	switch( (*p) ) {
		case 97u: goto tr5;
		case 100u: goto tr6;
		case 110u: goto tr7;
	}
	goto st0;
tr6:
#line 50 "build/packet_actions.rl"
	{
#ifdef VERBOSE_STATES
  std::cout << "[type_received]: " << static_cast<int>(*p) << std::endl;
#endif  // #ifdef VERBOSE_STATES
  packet_->type(*p);
}
	goto st6;
st6:
	if ( ++p == pe )
		goto _test_eof6;
case 6:
#line 297 "build/packet_actions.cpp"
	goto tr8;
tr8:
#line 57 "build/packet_actions.rl"
	{
#ifdef VERBOSE_STATES
  std::cout << "[length_received]: " << static_cast<int>(*p) << std::endl;
#endif  // #ifdef VERBOSE_STATES
#ifdef ARDUINO_DEBUG
  Serial.print("[len]: ");
  Serial.print(static_cast<int>(*p));
  Serial.print("/");
  Serial.println(packet_->buffer_size_);
#endif  // #ifdef ARDUINO_DEBUG
  payload_bytes_expected_ = *p;
  if (payload_bytes_expected_ > packet_->buffer_size_) {
#ifndef AVR
      std::cerr << "[ERROR]: expected length is too long for buffer.  "
                   "Buffer length is " << packet_->buffer_size_ << std::endl;
#endif  // #ifndef AVR
    parse_error_ = true;
  }
}
#line 62 "build/packet.rl"
	{ {stack[top++] = 7; goto st11;} }
	goto st7;
st7:
	if ( ++p == pe )
		goto _test_eof7;
case 7:
#line 327 "build/packet_actions.cpp"
	goto tr9;
tr9:
#line 117 "build/packet_actions.rl"
	{
#ifdef VERBOSE_STATES
  std::cout << "[payload_end] received: " << payload_bytes_received_ << "/"
            << payload_bytes_expected_ << std::endl;
#endif  // #ifdef VERBOSE_STATES
  crc_ = finalize_crc(crc_);
}
#line 125 "build/packet_actions.rl"
	{
#ifdef VERBOSE_STATES
  std::cout << "[crc_start]" << std::endl;
#endif  // #ifdef VERBOSE_STATES
  packet_->crc_ = 0;
}
#line 132 "build/packet_actions.rl"
	{
#ifdef VERBOSE_STATES
  std::cout << "[crc_byte_received]: " << std::hex << static_cast<int>(0x00FFFF & *p) << std::endl;
#endif  // #ifdef VERBOSE_STATES
  packet_->crc_ <<= 8;
  packet_->crc_ += *p;
}
	goto st8;
st8:
	if ( ++p == pe )
		goto _test_eof8;
case 8:
#line 358 "build/packet_actions.cpp"
	goto tr10;
tr7:
#line 50 "build/packet_actions.rl"
	{
#ifdef VERBOSE_STATES
  std::cout << "[type_received]: " << static_cast<int>(*p) << std::endl;
#endif  // #ifdef VERBOSE_STATES
  packet_->type(*p);
}
	goto st9;
st9:
	if ( ++p == pe )
		goto _test_eof9;
case 9:
#line 373 "build/packet_actions.cpp"
	goto tr11;
st11:
	if ( ++p == pe )
		goto _test_eof11;
case 11:
	goto tr13;
tr13:
#line 77 "build/packet_actions.rl"
	{
#ifdef VERBOSE_STATES
  std::cout << "[payload_start] expected size: " << payload_bytes_expected_
            << std::endl;
#endif  // #ifdef VERBOSE_STATES
#ifdef ARDUINO_DEBUG
  Serial.println("[payload]");
#endif  // #ifdef ARDUINO_DEBUG
  /* Resize the payload buffer to fit the expected payload size. */
  // packet_->reallocate_buffer(payload_bytes_expected_);
  // Reset received-bytes counter.
  payload_bytes_received_ = 0;
  crc_ = crc_init();
}
#line 92 "build/packet_actions.rl"
	{
#ifdef VERBOSE_STATES
  std::cout << "[payload_byte_received] byte: " << payload_bytes_received_
            << std::endl;
#endif  // #ifdef VERBOSE_STATES
#ifdef ARDUINO_DEBUG
  Serial.print("[b] [");
  Serial.print(static_cast<char>(*p));
  Serial.print("] byte: ");
  Serial.println(payload_bytes_received_);
#endif  // #ifdef ARDUINO_DEBUG
  /* We received another payload octet, so:
   *
   *   - Update CRC checksum.
   *   - Copy octet _(i.e. byte)_ to payload buffer of packet.
   *   - Increment received count.
   *   - Check if we've received all expected octets. */
  crc_ = update_crc(crc_, *p);
  packet_->payload_buffer_[payload_bytes_received_++] = *p;
  if (payload_bytes_received_ == payload_bytes_expected_) {
    /* We've received the expected number of payload octets. */
    {cs = stack[--top];goto _again;}
  }
}
	goto st12;
tr14:
#line 92 "build/packet_actions.rl"
	{
#ifdef VERBOSE_STATES
  std::cout << "[payload_byte_received] byte: " << payload_bytes_received_
            << std::endl;
#endif  // #ifdef VERBOSE_STATES
#ifdef ARDUINO_DEBUG
  Serial.print("[b] [");
  Serial.print(static_cast<char>(*p));
  Serial.print("] byte: ");
  Serial.println(payload_bytes_received_);
#endif  // #ifdef ARDUINO_DEBUG
  /* We received another payload octet, so:
   *
   *   - Update CRC checksum.
   *   - Copy octet _(i.e. byte)_ to payload buffer of packet.
   *   - Increment received count.
   *   - Check if we've received all expected octets. */
  crc_ = update_crc(crc_, *p);
  packet_->payload_buffer_[payload_bytes_received_++] = *p;
  if (payload_bytes_received_ == payload_bytes_expected_) {
    /* We've received the expected number of payload octets. */
    {cs = stack[--top];goto _again;}
  }
}
	goto st12;
st12:
	if ( ++p == pe )
		goto _test_eof12;
case 12:
#line 453 "build/packet_actions.cpp"
	goto tr14;
	}
	_test_eof10: cs = 10; goto _test_eof; 
	_test_eof1: cs = 1; goto _test_eof; 
	_test_eof2: cs = 2; goto _test_eof; 
	_test_eof3: cs = 3; goto _test_eof; 
	_test_eof4: cs = 4; goto _test_eof; 
	_test_eof5: cs = 5; goto _test_eof; 
	_test_eof6: cs = 6; goto _test_eof; 
	_test_eof7: cs = 7; goto _test_eof; 
	_test_eof8: cs = 8; goto _test_eof; 
	_test_eof9: cs = 9; goto _test_eof; 
	_test_eof11: cs = 11; goto _test_eof; 
	_test_eof12: cs = 12; goto _test_eof; 

	_test_eof: {}
	if ( p == eof )
	{
	switch ( cs ) {
	case 11: 
#line 77 "build/packet_actions.rl"
	{
#ifdef VERBOSE_STATES
  std::cout << "[payload_start] expected size: " << payload_bytes_expected_
            << std::endl;
#endif  // #ifdef VERBOSE_STATES
#ifdef ARDUINO_DEBUG
  Serial.println("[payload]");
#endif  // #ifdef ARDUINO_DEBUG
  /* Resize the payload buffer to fit the expected payload size. */
  // packet_->reallocate_buffer(payload_bytes_expected_);
  // Reset received-bytes counter.
  payload_bytes_received_ = 0;
  crc_ = crc_init();
}
	break;
#line 490 "build/packet_actions.cpp"
	}
	}

	_out: {}
	}

#line 245 "build/packet_actions.rl"

#ifdef ARDUINO_DEBUG
  Serial.print("[p] (");
  Serial.print(cs);
  Serial.print(") ");
  if (*byte > 20 && *byte < 128) {
    Serial.print("'");
    Serial.print(static_cast<char>(*byte));
    Serial.print("'");
  } else {
    Serial.print(static_cast<int>(*byte));
  }
  Serial.println("");
#endif  // #ifdef ARDUINO_DEBUG
}


template void PacketParser<FixedPacket>::reset();
template void PacketParser<FixedPacket>::parse_byte(uint8_t *);
