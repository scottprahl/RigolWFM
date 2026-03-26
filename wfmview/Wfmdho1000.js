// This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['exports', 'kaitai-struct/KaitaiStream'], factory);
  } else if (typeof exports === 'object' && exports !== null && typeof exports.nodeType !== 'number') {
    factory(exports, require('kaitai-struct/KaitaiStream'));
  } else {
    factory(root.Wfmdho1000 || (root.Wfmdho1000 = {}), root.KaitaiStream);
  }
})(typeof self !== 'undefined' ? self : this, function (Wfmdho1000_, KaitaiStream) {
/**
 * Proprietary waveform format used by Rigol DHO800/DHO1000 series
 * oscilloscopes (reverse-engineered from DHO1074 and DHO824 captures).
 * 
 * File layout:
 *   [File Header:      24 bytes  - partially unknown]
 *   [Metadata blocks:  variable  - 12-byte header + zlib-compressed content each]
 *   [Zero padding:     variable  - null bytes between block region and data]
 *   [Data section:     variable  - 40-byte header + uint16 ADC samples]
 * 
 * ---- Metadata blocks ----
 * Each block has a 12-byte header (six u16 LE fields) followed by len_content_raw
 * bytes of content.  When comp_size < decomp_size the content bytes
 * [0 .. comp_size-1] are zlib-compressed; the remainder is zero padding.
 * Blocks are read until a terminator block where len_content_raw == 0.
 * 
 * Key blocks (identified by block_id and block_type):
 *   block_id=1..4, block_type=9  (~88-96 bytes decompressed)
 *     Offset  1..8  - int64 LE - voltage scale numerator
 *     scale = i64 / 750_000_000_000
 *     Offset 38..45 - int64 LE - channel voltage centre x 1e8
 *     v_center = i64 / 1e8
 * 
 *   block_type=6  (~1628 bytes decompressed)
 *     Offset 36..39 - int32 LE - CH1 voltage centre x 1e8
 *     Legacy fallback for older single-channel captures.
 * 
 * ---- Voltage calibration ----
 *   scale    = i64_channel / 750_000_000_000
 *   v_center = i64_channel / 1e8
 *   offset   = -v_center - scale * 32768
 *   volts[i] = scale * raw_uint16[i] + offset
 * 
 * ---- Data section ----
 * The data section starts after the zero-padding region that follows the
 * last metadata block.  Its offset cannot be determined statically; a
 * sequential scan for the first non-zero byte is required.
 * 
 * Data section header (40 bytes):
 *   offset+ 0:  u64 LE  - raw total sample count across all enabled channels.
 *                          DHO1000 firmware stores a value slightly larger than
 *                          the true total (~+64 samples); n_ch is recovered via
 *                          round(n_pts_u64 / n_pts_per_channel) rather than
 *                          exact division.
 *   offset+ 8:  8 bytes - capture marker (opaque)
 *   offset+16:  u32 LE  - x_increment in ADC ticks (see below)
 *   offset+20:  u32 LE  - unknown (observed: 77)
 *   offset+24:  u32 LE  - n_pts per enabled channel
 *   offset+28:  u32 LE  - n_pts per enabled channel (repeated)
 *   offset+32:  u32 LE  - timestamp / unknown
 *   offset+36:  u32 LE  - unknown (observed: 120 for single-channel, 0 for multi)
 *   offset+40:  uint16 LE samples begin (n_pts_per_channel × n_channels × 2 bytes)
 * 
 * ---- Time axis ----
 * The x_increment field stores the sampling interval as an integer count of
 * ADC clock ticks.  The tick duration is a fixed hardware property:
 * 
 *   DHO800  (e.g. DHO824):  0.8 ns / tick  — one cycle of the 1.25 GSa/s ADC
 *   DHO1000 (e.g. DHO1074): 10 ns / tick   — one cycle of a 100 MHz reference clock
 * 
 * x_origin is not stored explicitly.  For the common case of a centered
 * trigger (trigger at 50% of the capture window, which is the scope default):
 *   x_origin = -(n_pts_per_channel / 2) * x_increment
 *   t[i]     =  x_origin + i * x_increment
 * 
 * Trigger position as a percentage of the capture window is likely encoded
 * in the metadata block with id=282, u32 at byte offset 12 (observed: 50 for
 * center trigger in all available DHO800 and DHO1000 test captures).
 * 
 * LIMITATION: This KSY describes the block region only.  The zero-padding
 * region and the data section require sequential runtime scanning and cannot
 * be expressed as fixed-offset KSY instances.
 */

var Wfmdho1000 = (function() {
  Wfmdho1000.BlockTypeEnum = Object.freeze({
    DHO800_CHANNEL_PARAMS: 5,
    SETTINGS: 6,
    CHANNEL_PARAMS: 9,

    5: "DHO800_CHANNEL_PARAMS",
    6: "SETTINGS",
    9: "CHANNEL_PARAMS",
  });

  function Wfmdho1000(_io, _parent, _root) {
    this._io = _io;
    this._parent = _parent;
    this._root = _root || this;

    this._read();
  }
  Wfmdho1000.prototype._read = function() {
    this.fileHeader = new FileHeader(this._io, this, this._root);
    this.blocks = [];
    var i = 0;
    do {
      var _ = new Block(this._io, this, this._root);
      this.blocks.push(_);
      i++;
    } while (!( ((_.lenContentRaw == 0) && (_.compSize == 0)) ));
  }

  /**
   * One metadata block.  A block with len_content_raw == 0 and comp_size == 0
   * signals the end of the metadata region.
   */

  var Block = Wfmdho1000.Block = (function() {
    function Block(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    Block.prototype._read = function() {
      this.blockId = this._io.readU2le();
      this.blockType = this._io.readU2le();
      this.decompSize = this._io.readU2le();
      this.compSize = this._io.readU2le();
      this.lenContentRaw = this._io.readU2le();
      this.reserved = this._io.readU2le();
      this.contentRaw = this._io.readBytes(this.lenContentRaw);
    }

    /**
     * True for one of the per-channel parameter blocks.
     * Decompressed content bytes [1..8] hold an int64 LE voltage scale
     * numerator, and bytes [38..45] hold an int64 LE channel center.
     */
    Object.defineProperty(Block.prototype, 'isChannelParams', {
      get: function() {
        if (this._m_isChannelParams !== undefined)
          return this._m_isChannelParams;
        this._m_isChannelParams =  ((this.blockType == Wfmdho1000.BlockTypeEnum.CHANNEL_PARAMS) && (this.blockId >= 1) && (this.blockId <= 4)) ;
        return this._m_isChannelParams;
      }
    });

    /**
     * True for the trigger/display settings block.
     * Decompressed content bytes [36..39] hold an int32 LE voltage centre
     * value: v_center = i32 / 1e8.
     */
    Object.defineProperty(Block.prototype, 'isSettings', {
      get: function() {
        if (this._m_isSettings !== undefined)
          return this._m_isSettings;
        this._m_isSettings = this.blockType == Wfmdho1000.BlockTypeEnum.SETTINGS;
        return this._m_isSettings;
      }
    });

    /**
     * True for the sentinel block that ends the metadata region.
     */
    Object.defineProperty(Block.prototype, 'isTerminator', {
      get: function() {
        if (this._m_isTerminator !== undefined)
          return this._m_isTerminator;
        this._m_isTerminator =  ((this.lenContentRaw == 0) && (this.compSize == 0)) ;
        return this._m_isTerminator;
      }
    });

    /**
     * Channel / block identifier.
     * 1..4 = analog channel parameters for CH1..CH4 when block_type == 9.
     */

    /**
     * Content type.
     * 9 = channel parameters.
     * 6 = trigger/display settings (legacy CH1 v_center fallback).
     */

    /**
     * Decompressed content size in bytes.
     */

    /**
     * Compressed content size in bytes.
     * Equal to decomp_size when content is stored verbatim (not compressed).
     */

    /**
     * Total bytes consumed in the file for this block's content
     * (comp_size rounded up to the next alignment boundary).
     * Zero in the terminator block.
     */

    /**
     * Always 0.
     */

    /**
     * Block content bytes.  The first comp_size bytes hold the payload
     * (zlib-compressed when comp_size != decomp_size; verbatim otherwise).
     * Remaining bytes (len_content_raw - comp_size) are zero padding.
     */

    return Block;
  })();

  /**
   * DHO1000 per-channel parameter payload after optional zlib decompression.
   * Observed channel blocks store the displayed vertical center with the
   * opposite sign from the sample reconstruction offset.
   */

  var Dho1000ChannelParams = Wfmdho1000.Dho1000ChannelParams = (function() {
    function Dho1000ChannelParams(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    Dho1000ChannelParams.prototype._read = function() {
      this.reserved0 = this._io.readBytes(1);
      this.scaleNumerator = this._io.readS8le();
      this.reserved1 = this._io.readBytes(29);
      this.vCenterRaw = this._io.readS8le();
      this.reserved2 = this._io.readBytesFull();
    }
    Object.defineProperty(Dho1000ChannelParams.prototype, 'offset', {
      get: function() {
        if (this._m_offset !== undefined)
          return this._m_offset;
        this._m_offset = -(this.vCenter) - this.scale * 32768;
        return this._m_offset;
      }
    });
    Object.defineProperty(Dho1000ChannelParams.prototype, 'scale', {
      get: function() {
        if (this._m_scale !== undefined)
          return this._m_scale;
        this._m_scale = this.scaleNumerator / 750000000000.0;
        return this._m_scale;
      }
    });
    Object.defineProperty(Dho1000ChannelParams.prototype, 'vCenter', {
      get: function() {
        if (this._m_vCenter !== undefined)
          return this._m_vCenter;
        this._m_vCenter = this.vCenterRaw / 1.0E+8;
        return this._m_vCenter;
      }
    });

    return Dho1000ChannelParams;
  })();

  /**
   * DHO800 per-channel parameter payload after optional zlib decompression.
   * The stored center value is negated and scaled in 1e-9 volt units.
   */

  var Dho800ChannelParams = Wfmdho1000.Dho800ChannelParams = (function() {
    function Dho800ChannelParams(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    Dho800ChannelParams.prototype._read = function() {
      this.reserved0 = this._io.readBytes(1);
      this.scaleNumerator = this._io.readS8le();
      this.reserved1 = this._io.readBytes(29);
      this.vCenterRaw = this._io.readS4le();
      this.reserved2 = this._io.readBytesFull();
    }
    Object.defineProperty(Dho800ChannelParams.prototype, 'offset', {
      get: function() {
        if (this._m_offset !== undefined)
          return this._m_offset;
        this._m_offset = this.vCenter - this.scale * 32768;
        return this._m_offset;
      }
    });
    Object.defineProperty(Dho800ChannelParams.prototype, 'scale', {
      get: function() {
        if (this._m_scale !== undefined)
          return this._m_scale;
        this._m_scale = this.scaleNumerator / 7500000000000.0;
        return this._m_scale;
      }
    });
    Object.defineProperty(Dho800ChannelParams.prototype, 'vCenter', {
      get: function() {
        if (this._m_vCenter !== undefined)
          return this._m_vCenter;
        this._m_vCenter = -(this.vCenterRaw) / 1.0E+9;
        return this._m_vCenter;
      }
    });

    return Dho800ChannelParams;
  })();

  /**
   * 24-byte file header.  Internal structure not fully reverse-engineered;
   * treated as opaque.
   */

  var FileHeader = Wfmdho1000.FileHeader = (function() {
    function FileHeader(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    FileHeader.prototype._read = function() {
      this.reserved = this._io.readBytes(24);
    }

    /**
     * File header bytes - internal layout not yet fully known.
     */

    return FileHeader;
  })();

  /**
   * Trigger/display settings payload after optional zlib decompression.
   * Older single-channel captures expose only the CH1 vertical center here.
   */

  var SettingsBlock = Wfmdho1000.SettingsBlock = (function() {
    function SettingsBlock(_io, _parent, _root) {
      this._io = _io;
      this._parent = _parent;
      this._root = _root;

      this._read();
    }
    SettingsBlock.prototype._read = function() {
      this.reserved0 = this._io.readBytes(36);
      this.vCenterRaw = this._io.readS4le();
      this.reserved1 = this._io.readBytesFull();
    }
    Object.defineProperty(SettingsBlock.prototype, 'vCenter', {
      get: function() {
        if (this._m_vCenter !== undefined)
          return this._m_vCenter;
        this._m_vCenter = this.vCenterRaw / 1.0E+8;
        return this._m_vCenter;
      }
    });

    return SettingsBlock;
  })();

  /**
   * Metadata blocks terminated by an all-zero block header.
   */

  return Wfmdho1000;
})();
Wfmdho1000_.Wfmdho1000 = Wfmdho1000;
});
