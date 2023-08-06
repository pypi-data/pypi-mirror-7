#! /usr/bin/env python

from cstruct import CStruct

class Ehdr(CStruct):
    _fields = [ ("ident","16s"),
                ("type","u16"),
                ("machine","u16"),
                ("version","u32"),
                ("entry","ptr"),
                ("phoff","ptr"),
                ("shoff","ptr"),
                ("flags","u32"),
                ("ehsize","u16"),
                ("phentsize","u16"),
                ("phnum","u16"),
                ("shentsize","u16"),
                ("shnum","u16"),
                ("shstrndx","u16") ]


class Shdr(CStruct):
    _fields = [ ("name","u32"),
                ("type","u32"),
                ("flags","ptr"),
                ("addr","ptr"),
                ("offset","ptr"),
                ("size","ptr"),
                ("link","u32"),
                ("info","u32"),
                ("addralign","ptr"),
                ("entsize","ptr") ]

class Phdr(CStruct):
    _fields = [ ("type","u32"),
                ("offset","u32"),
                ("vaddr","u32"),
                ("paddr","u32"),
                ("filesz","u32"),
                ("memsz","u32"),
                ("flags","u32"),
                ("align","u32") ]

class Phdr64(CStruct):
    _fields = [ ("type","u32"),
                ("flags","u32"),
                ("offset","ptr"),
                ("vaddr","ptr"),
                ("paddr","ptr"),
                ("filesz","ptr"),
                ("memsz","ptr"),
                ("align","ptr") ]


class Sym32(CStruct):
    _fields = [ ("name","u32"),
                ("value","u32"),
                ("size","u32"),
                ("info","u08"),
                ("other","u08"),
                ("shndx","u16") ]

class Sym64(CStruct):
    _fields = [ ("name","u32"),
                ("info","u08"),
                ("other","u08"),
                ("shndx","u16"),
                ("value","u32"),
                ("size","u64") ]

class Dym(CStruct):
    _fields = [ ("tag","u32"),
                ("val","u32") ]

class Rel32(CStruct):
    _packformat = "="
    _fields = [ ("offset","ptr"),
                ("type","u08"),
                ("sym","u16"),
                ("zero","u08") ]

class Rel64(CStruct):
    _packformat = "="
    _fields = [ ("offset","ptr"),
                ("type","u32"),
                ("sym","u32") ]

class Rela32(CStruct):
    _packformat = "="
    _fields = [ ("offset","ptr"),
                ("type","u08"),
                ("sym","u08"),
                ("zero","u16"),
                ("addend","ptr") ]

class Rela64(CStruct):
    _packformat = "="
    _fields = [ ("offset","ptr"),
                ("type","u32"),
                ("sym","u32"),
                ("addend","ptr") ]

class Dynamic(CStruct):
    _fields = [ ("type","u32"),
                ("name","u32") ]


# Legal values for e_ident (identification indexes)

EI_MAG0	=       0	# File identification
EI_MAG1	=       1	# File identification
EI_MAG2	=       2	# File identification
EI_MAG3	=       3	# File identification
EI_CLASS =      4	# File class
EI_DATA	=       5	# Data encoding
EI_VERSION =    6	# File version
EI_OSABI =      7	# Operating system/ABI identification
EI_ABIVERSION = 8	# ABI version
EI_PAD =        9	# Start of padding bytes
EI_NIDENT =     16	# Size of e_ident[]

# Legal values for e_ident[EI_CLASS]

ELFCLASSNONE =  0	# Invalid class
ELFCLASS32 =	1	# 32-bit objects
ELFCLASS64 =    2	# 64-bit objects

# Legal values for e_ident[EI_DATA]

ELFDATANONE =	0	# Invalid data encoding
ELFDATA2LSB =	1	# Least significant byte at lowest address
ELFDATA2MSB =	2	# Most significant byte at lowest address

# Legal values for e_type (object file type).

ET_NONE =         0               # No file type
ET_REL =          1               # Relocatable file
ET_EXEC =         2               # Executable file
ET_DYN =          3               # Shared object file
ET_CORE =         4               # Core file
ET_NUM =          5               # Number of defined types
ET_LOOS =         0xfe00L         # OS-specific range start
ET_HIOS =         0xfeffL         # OS-specific range end
ET_LOPROC =       0xff00L         # Processor-specific range start
ET_HIPROC =       0xffffL         # Processor-specific range end

# Legal values for e_machine (architecture).

EM_NONE =         0              # No machine
EM_M32 =          1              # AT&T WE 32100
EM_SPARC =        2              # SUN SPARC
EM_386 =          3              # Intel 80386
EM_68K =          4              # Motorola m68k family
EM_88K =          5              # Motorola m88k family
EM_486 =          6              # Intel 80486
EM_860 =          7              # Intel 80860
EM_MIPS =         8              # MIPS R3000 big-endian
EM_S370 =         9              # IBM System/370
EM_MIPS_RS3_LE = 10              # MIPS R3000 little-endian

EM_PARISC =      15              # HPPA
EM_VPP500 =      17              # Fujitsu VPP500
EM_SPARC32PLUS = 18              # Sun's "v8plus"
EM_960 =         19              # Intel 80960
EM_PPC =         20              # PowerPC
EM_PPC64 =       21              # PowerPC 64-bit
EM_S390 =        22              # IBM S390

EM_V800 =        36              # NEC V800 series
EM_FR20 =        37              # Fujitsu FR20
EM_RH32 =        38              # TRW RH-32
EM_RCE =         39              # Motorola RCE
EM_ARM =         40              # ARM
EM_FAKE_ALPHA =  41              # Digital Alpha
EM_SH =          42              # Hitachi SH
EM_SPARCV9 =     43              # SPARC v9 64-bit
EM_TRICORE =     44              # Siemens Tricore
EM_ARC =         45              # Argonaut RISC Core
EM_H8_300 =      46              # Hitachi H8/300
EM_H8_300H =     47              # Hitachi H8/300H
EM_H8S =         48              # Hitachi H8S
EM_H8_500 =      49              # Hitachi H8/500
EM_IA_64 =       50              # Intel Merced
EM_MIPS_X =      51              # Stanford MIPS-X
EM_COLDFIRE =    52              # Motorola Coldfire
EM_68HC12 =      53              # Motorola M68HC12
EM_MMA =         54              # Fujitsu MMA Multimedia Accelerator*/
EM_PCP =         55              # Siemens PCP
EM_NCPU =        56              # Sony nCPU embeeded RISC
EM_NDR1 =        57              # Denso NDR1 microprocessor
EM_STARCORE =    58              # Motorola Start*Core processor
EM_ME16 =        59              # Toyota ME16 processor
EM_ST100 =       60              # STMicroelectronic ST100 processor
EM_TINYJ =       61              # Advanced Logic Corp. Tinyj emb.fam*/
EM_X86_64 =      62              # AMD x86-64 architecture
EM_PDSP =        63              # Sony DSP Processor

EM_FX66 =        66              # Siemens FX66 microcontroller
EM_ST9PLUS =     67              # STMicroelectronics ST9+ 8/16 mc
EM_ST7 =         68              # STmicroelectronics ST7 8 bit mc
EM_68HC16 =      69              # Motorola MC68HC16 microcontroller
EM_68HC11 =      70              # Motorola MC68HC11 microcontroller
EM_68HC08 =      71              # Motorola MC68HC08 microcontroller
EM_68HC05 =      72              # Motorola MC68HC05 microcontroller
EM_SVX =         73              # Silicon Graphics SVx
EM_ST19 =        74              # STMicroelectronics ST19 8 bit mc
EM_VAX =         75              # Digital VAX
EM_CRIS =        76              # Axis Communications 32-bit embedded processor
EM_JAVELIN =     77              # Infineon Technologies 32-bit embedded processor
EM_FIREPATH =    78              # Element 14 64-bit DSP Processor
EM_ZSP =         79              # LSI Logic 16-bit DSP Processor
EM_MMIX =        80              # Donald Knuth's educational 64-bit processor
EM_HUANY =       81              # Harvard University machine-independent object files
EM_PRISM =       82              # SiTera Prism
EM_AVR =         83              # Atmel AVR 8-bit microcontroller
EM_FR30 =        84              # Fujitsu FR30
EM_D10V =        85              # Mitsubishi D10V
EM_D30V =        86              # Mitsubishi D30V
EM_V850 =        87              # NEC v850
EM_M32R =        88              # Mitsubishi M32R
EM_MN10300 =     89              # Matsushita MN10300
EM_MN10200 =     90              # Matsushita MN10200
EM_PJ =          91              # picoJava
EM_OPENRISC =    92              # OpenRISC 32-bit embedded processor
EM_ARC_A5 =      93              # ARC Cores Tangent-A5
EM_XTENSA =      94              # Tensilica Xtensa Architecture

EM_ALPHA =       0x9026

# Legal values for sh_type (section type).

SHT_NULL =          0             # Section header table entry unused
SHT_PROGBITS =      1             # Program data
SHT_SYMTAB =        2             # Symbol table
SHT_STRTAB =        3             # String table
SHT_RELA =          4             # Relocation entries with addends
SHT_HASH =          5             # Symbol hash table
SHT_DYNAMIC =       6             # Dynamic linking information
SHT_NOTE =          7             # Notes
SHT_NOBITS =        8             # Program space with no data (bss)
SHT_REL =           9             # Relocation entries, no addends
SHT_SHLIB =         10            # Reserved
SHT_DYNSYM =        11            # Dynamic linker symbol table
SHT_INIT_ARRAY =    14            # Array of constructors
SHT_FINI_ARRAY =    15            # Array of destructors
SHT_PREINIT_ARRAY = 16            # Array of pre-constructors
SHT_GROUP =         17            # Section group
SHT_SYMTAB_SHNDX =  18            # Extended section indeces
SHT_NUM =           19            # Number of defined types.
SHT_LOOS =          0x60000000L   # Start OS-specific
SHT_GNU_LIBLIST =   0x6ffffff7L   # Prelink library list
SHT_CHECKSUM =      0x6ffffff8L   # Checksum for DSO content.
SHT_LOSUNW =        0x6ffffffaL   # Sun-specific low bound.
SHT_SUNW_move =     0x6ffffffaL
SHT_SUNW_COMDAT =   0x6ffffffbL
SHT_SUNW_syminfo =  0x6ffffffcL
SHT_GNU_verdef =    0x6ffffffdL   # Version definition section.
SHT_GNU_verneed =   0x6ffffffeL   # Version needs section.
SHT_GNU_versym =    0x6fffffffL   # Version symbol table.
SHT_HISUNW =        0x6fffffffL   # Sun-specific high bound.
SHT_HIOS =          0x6fffffffL   # End OS-specific type
SHT_LOPROC =        0x70000000L   # Start of processor-specific
SHT_HIPROC =        0x7fffffffL   # End of processor-specific
SHT_LOUSER =        0x80000000L   # Start of application-specific
SHT_HIUSER =        0x8fffffffL   # End of application-specific

# Legal values for sh_flags (section flags).

SHF_WRITE =            (1 << 0)   # Writable
SHF_ALLOC =            (1 << 1)   # Occupies memory during execution
SHF_EXECINSTR =        (1 << 2)   # Executable
SHF_MERGE =            (1 << 4)   # Might be merged
SHF_STRINGS =          (1 << 5)   # Contains nul-terminated strings
SHF_INFO_LINK =        (1 << 6)   # `sh_info' contains SHT index
SHF_LINK_ORDER =       (1 << 7)   # Preserve order after combining
SHF_OS_NONCONFORMING = (1 << 8)   # Non-standard OS specific handling required
SHF_GROUP =           (1 << 9)    # Section is member of a group.
SHF_TLS =             (1 << 10)   # Section hold thread-local data.
SHF_MASKOS =          0x0ff00000L # OS-specific.
SHF_MASKPROC =        0xf0000000L # Processor-specific

# Section group handling.

GRP_COMDAT =      0x1             # Mark group as COMDAT.

# Legal values for p_type (segment type).

PT_NULL =         0               # Program header table entry unused
PT_LOAD =         1               # Loadable program segment
PT_DYNAMIC =      2               # Dynamic linking information
PT_INTERP =       3               # Program interpreter
PT_NOTE =         4               # Auxiliary information
PT_SHLIB =        5               # Reserved
PT_PHDR =         6               # Entry for header table itself
PT_TLS =          7               # Thread-local storage segment
PT_NUM =          8               # Number of defined types
PT_LOOS =         0x60000000L     # Start of OS-specific
PT_GNU_EH_FRAME = 0x6474e550L     # GCC .eh_frame_hdr segment
PT_GNU_STACK =    0x6474e551L     # Indicates stack executability
PT_LOSUNW =       0x6ffffffaL
PT_SUNWBSS =      0x6ffffffaL     # Sun Specific segment
PT_SUNWSTACK =    0x6ffffffbL     # Stack segment
PT_HISUNW =       0x6fffffffL
PT_HIOS =         0x6fffffffL     # End of OS-specific
PT_LOPROC =       0x70000000L     # Start of processor-specific
PT_HIPROC =       0x7fffffffL     # End of processor-specific

# Legal values for p_flags (segment flags).

PF_X =            (1 << 0)        # Segment is executable
PF_W =            (1 << 1)        # Segment is writable
PF_R =            (1 << 2)        # Segment is readable
PF_MASKOS =       0x0ff00000L     # OS-specific
PF_MASKPROC =     0xf0000000L     # Processor-specific

# Legal values for note segment descriptor types for core files.

NT_PRSTATUS =     1               # Contains copy of prstatus struct
NT_FPREGSET =     2               # Contains copy of fpregset struct
NT_PRPSINFO =     3               # Contains copy of prpsinfo struct
NT_PRXREG =       4               # Contains copy of prxregset struct
NT_TASKSTRUCT =   4               # Contains copy of task structure
NT_PLATFORM =     5               # String from sysinfo(SI_PLATFORM)
NT_AUXV =         6               # Contains copy of auxv array
NT_GWINDOWS =     7               # Contains copy of gwindows struct
NT_ASRS =         8               # Contains copy of asrset struct
NT_PSTATUS =      10              # Contains copy of pstatus struct
NT_PSINFO =       13              # Contains copy of psinfo struct
NT_PRCRED =       14              # Contains copy of prcred struct
NT_UTSNAME =      15              # Contains copy of utsname struct
NT_LWPSTATUS =    16              # Contains copy of lwpstatus struct
NT_LWPSINFO =     17              # Contains copy of lwpinfo struct
NT_PRFPXREG =     20              # Contains copy of fprxregset struct

# Legal values for the note segment descriptor types for object files.

NT_VERSION =      1               # Contains a version string.

# Legal values for ST_BIND subfield of st_info (symbol binding).
# bind = Sym.info >> 4
# val = Sym.info 0xf

STB_LOCAL       = 0               # Local symbol
STB_GLOBAL      = 1               # Global symbol
STB_WEAK        = 2               # Weak symbol
STB_NUM         = 3               # Number of defined types.
STB_LOOS        = 10              # Start of OS-specific
STB_HIOS        = 12              # End of OS-specific
STB_LOPROC      = 13              # Start of processor-specific
STB_HIPROC      = 15              # End of processor-specific

#Legal values for ST_TYPE subfield of st_info (symbol type).

STT_NOTYPE      = 0               # Symbol type is unspecified
STT_OBJECT      = 1               # Symbol is a data object
STT_FUNC        = 2               # Symbol is a code object
STT_SECTION     = 3               # Symbol associated with a section
STT_FILE        = 4               # Symbol's name is file name
STT_COMMON      = 5               # Symbol is a common data object
STT_TLS         = 6               # Symbol is thread-local data object*/
STT_NUM         = 7               # Number of defined types.
STT_LOOS        = 10              # Start of OS-specific
STT_HIOS        = 12              # End of OS-specific
STT_LOPROC      = 13              # Start of processor-specific
STT_HIPROC      = 15              # End of processor-specific

# Legal values for d_tag (dynamic entry type).

DT_NULL         = 0               # Marks end of dynamic section
DT_NEEDED       = 1               # Name of needed library
DT_PLTRELSZ     = 2               # Size in bytes of PLT relocs
DT_PLTGOT       = 3               # Processor defined value
DT_HASH         = 4               # Address of symbol hash table
DT_STRTAB       = 5               # Address of string table
DT_SYMTAB       = 6               # Address of symbol table
DT_RELA         = 7               # Address of Rela relocs
DT_RELASZ       = 8               # Total size of Rela relocs
DT_RELAENT      = 9               # Size of one Rela reloc
DT_STRSZ        = 10              # Size of string table
DT_SYMENT       = 11              # Size of one symbol table entry
DT_INIT         = 12              # Address of init function
DT_FINI         = 13              # Address of termination function
DT_SONAME       = 14              # Name of shared object
DT_RPATH        = 15              # Library search path (deprecated)
DT_SYMBOLIC     = 16              # Start symbol search here
DT_REL          = 17              # Address of Rel relocs
DT_RELSZ        = 18              # Total size of Rel relocs
DT_RELENT       = 19              # Size of one Rel reloc
DT_PLTREL       = 20              # Type of reloc in PLT
DT_DEBUG        = 21              # For debugging; unspecified
DT_TEXTREL      = 22              # Reloc might modify .text
DT_JMPREL       = 23              # Address of PLT relocs
DT_BIND_NOW     = 24              # Process relocations of object
DT_INIT_ARRAY   = 25              # Array with addresses of init fct
DT_FINI_ARRAY   = 26              # Array with addresses of fini fct
DT_INIT_ARRAYSZ = 27              # Size in bytes of DT_INIT_ARRAY
DT_FINI_ARRAYSZ = 28              # Size in bytes of DT_FINI_ARRAY
DT_RUNPATH      = 29              # Library search path
DT_FLAGS        = 30              # Flags for the object being loaded
DT_ENCODING     = 32              # Start of encoded range
DT_PREINIT_ARRAY = 32             # Array with addresses of preinit fct
DT_PREINIT_ARRAYSZ = 33           # size in bytes of DT_PREINIT_ARRAY
DT_NUM          = 34              # Number used
DT_LOOS         = 0x6000000d      # Start of OS-specific
DT_HIOS         = 0x6ffff000      # End of OS-specific
DT_LOPROC       = 0x70000000      # Start of processor-specific
DT_HIPROC       = 0x7fffffff      # End of processor-specific
#DT_PROCNUM      = DT_MIPS_NUM     # Most used by any processor

# DT_* entries which fall between DT_VALRNGHI & DT_VALRNGLO use the
# Dyn.d_un.d_val field of the Elf*_Dyn structure.  This follows Sun's
# approach.
DT_VALRNGLO     = 0x6ffffd00
DT_GNU_PRELINKED = 0x6ffffdf5     # Prelinking timestamp
DT_GNU_CONFLICTSZ = 0x6ffffdf6    # Size of conflict section
DT_GNU_LIBLISTSZ = 0x6ffffdf7     # Size of library list
DT_CHECKSUM     = 0x6ffffdf8
DT_PLTPADSZ     = 0x6ffffdf9
DT_MOVEENT      = 0x6ffffdfa
DT_MOVESZ       = 0x6ffffdfb
DT_FEATURE_1    = 0x6ffffdfc      # Feature selection (DTF_*).
DT_POSFLAG_1    = 0x6ffffdfd      # Flags for DT_* entries, effecting the following DT_* entry.
DT_SYMINSZ      = 0x6ffffdfe      # Size of syminfo table (in bytes)
DT_SYMINENT     = 0x6ffffdff      # Entry size of syminfo
DT_VALRNGHI     = 0x6ffffdff
DT_VALNUM = 12

# DT_* entries which fall between DT_ADDRRNGHI & DT_ADDRRNGLO use the
# Dyn.d_un.d_ptr field of the Elf*_Dyn structure.
#
# If any adjustment is made to the ELF object after it has been
# built these entries will need to be adjusted.
DT_ADDRRNGLO    = 0x6ffffe00
DT_GNU_CONFLICT = 0x6ffffef8      # Start of conflict section
DT_GNU_LIBLIST  = 0x6ffffef9      # Library list
DT_CONFIG       = 0x6ffffefa      # Configuration information.
DT_DEPAUDIT     = 0x6ffffefb      # Dependency auditing.
DT_AUDIT        = 0x6ffffefc      # Object auditing.
DT_PLTPAD       = 0x6ffffefd      # PLT padding.
DT_MOVETAB      = 0x6ffffefe      # Move table.
DT_SYMINFO      = 0x6ffffeff      # Syminfo table.
DT_ADDRRNGHI    = 0x6ffffeff
DT_ADDRNUM = 10

# The versioning entry types.  The next are defined as part of the
# GNU extension.
DT_VERSYM       = 0x6ffffff0

DT_RELACOUNT    = 0x6ffffff9
DT_RELCOUNT     = 0x6ffffffa

# These were chosen by Sun.
DT_FLAGS_1      = 0x6ffffffb      # State flags, see DF_1_* below.
DT_VERDEF       = 0x6ffffffc      # Address of version definition table
DT_VERDEFNUM    = 0x6ffffffd      # Number of version definitions
DT_VERNEED      = 0x6ffffffe      # Address of table with needed versions
DT_VERNEEDNUM   = 0x6fffffff      # Number of needed versions
DT_VERSIONTAGNUM = 16

# Sun added these machine-independent extensions in the "processor-specific"
# range.  Be compatible.
DT_AUXILIARY    = 0x7ffffffd      # Shared object to load before self
DT_FILTER       = 0x7fffffff      # Shared object to get values from
DT_EXTRANUM     = 3

# Values of `d_un.d_val' in the DT_FLAGS entry.
DF_ORIGIN       = 0x00000001      # Object may use DF_ORIGIN
DF_SYMBOLIC     = 0x00000002      # Symbol resolutions starts here
DF_TEXTREL      = 0x00000004      # Object contains text relocations
DF_BIND_NOW     = 0x00000008      # No lazy binding for this object
DF_STATIC_TLS   = 0x00000010      # Module uses the static TLS model

# State flags selectable in the `d_un.d_val' element of the DT_FLAGS_1
# entry in the dynamic section.
DF_1_NOW        = 0x00000001      # Set RTLD_NOW for this object.
DF_1_GLOBAL     = 0x00000002      # Set RTLD_GLOBAL for this object.
DF_1_GROUP      = 0x00000004      # Set RTLD_GROUP for this object.
DF_1_NODELETE   = 0x00000008      # Set RTLD_NODELETE for this object.
DF_1_LOADFLTR   = 0x00000010      # Trigger filtee loading at runtime.
DF_1_INITFIRST  = 0x00000020      # Set RTLD_INITFIRST for this object
DF_1_NOOPEN     = 0x00000040      # Set RTLD_NOOPEN for this object.
DF_1_ORIGIN     = 0x00000080      # $ORIGIN must be handled.
DF_1_DIRECT     = 0x00000100      # Direct binding enabled.
DF_1_TRANS      = 0x00000200
DF_1_INTERPOSE  = 0x00000400      # Object is used to interpose.
DF_1_NODEFLIB   = 0x00000800      # Ignore default lib search path.
DF_1_NODUMP     = 0x00001000      # Object can't be dldump'ed.
DF_1_CONFALT    = 0x00002000      # Configuration alternative created.
DF_1_ENDFILTEE  = 0x00004000      # Filtee terminates filters search.
DF_1_DISPRELDNE = 0x00008000      # Disp reloc applied at build time.
DF_1_DISPRELPND = 0x00010000      # Disp reloc applied at run-time.

# Flags for the feature selection in DT_FEATURE_1.
DTF_1_PARINIT   = 0x00000001
DTF_1_CONFEXP   = 0x00000002

# Flags in the DT_POSFLAG_1 entry effecting only the next DT_* entry.
DF_P1_LAZYLOAD  = 0x00000001      # Lazyload following object.
DF_P1_GROUPPERM = 0x00000002      # Symbols from next object are not generally available.


# Intel 80386 specific definitions.

# i386 relocs.

R_386_NONE         = 0            # No reloc
R_386_32           = 1            # Direct 32 bit
R_386_PC32         = 2            # PC relative 32 bit
R_386_GOT32        = 3            # 32 bit GOT entry
R_386_PLT32        = 4            # 32 bit PLT address
R_386_COPY         = 5            # Copy symbol at runtime
R_386_GLOB_DAT     = 6            # Create GOT entry
R_386_JMP_SLOT     = 7            # Create PLT entry
R_386_RELATIVE     = 8            # Adjust by program base
R_386_GOTOFF       = 9            # 32 bit offset to GOT
R_386_GOTPC        = 10           # 32 bit PC relative offset to GOT
R_386_32PLT        = 11
R_386_TLS_TPOFF    = 14           # Offset in static TLS block
R_386_TLS_IE       = 15           # Address of GOT entry for static TLS block offset
R_386_TLS_GOTIE    = 16           # GOT entry for static TLS block offset
R_386_TLS_LE       = 17           # Offset relative to static TLS block
R_386_TLS_GD       = 18           # Direct 32 bit for GNU version of general dynamic thread local data
R_386_TLS_LDM      = 19           # Direct 32 bit for GNU version of local dynamic thread local data in LE code
R_386_16           = 20
R_386_PC16         = 21
R_386_8            = 22
R_386_PC8          = 23
R_386_TLS_GD_32    = 24           # Direct 32 bit for general dynamic thread local data
R_386_TLS_GD_PUSH  = 25           # Tag for pushl in GD TLS code
R_386_TLS_GD_CALL  = 26           # Relocation for call to __tls_get_addr()
R_386_TLS_GD_POP   = 27           # Tag for popl in GD TLS code
R_386_TLS_LDM_32   = 28           # Direct 32 bit for local dynamic thread local data in LE code
R_386_TLS_LDM_PUSH = 29           # Tag for pushl in LDM TLS code
R_386_TLS_LDM_CALL = 30           # Relocation for call to __tls_get_addr() in LDM code
R_386_TLS_LDM_POP  = 31           # Tag for popl in LDM TLS code
R_386_TLS_LDO_32   = 32           # Offset relative to TLS block
R_386_TLS_IE_32    = 33           # GOT entry for negated static TLS block offset
R_386_TLS_LE_32    = 34           # Negated offset relative to static TLS block
R_386_TLS_DTPMOD32 = 35           # ID of module containing symbol
R_386_TLS_DTPOFF32 = 36           # Offset in TLS block
R_386_TLS_TPOFF32  = 37           # Negated offset in static TLS block
# Keep this the last entry.
R_386_NUM          = 38

if __name__ == "__main__":
    import sys
    ELFFILE = sys.stdin
    if len(sys.argv) > 1:
        ELFFILE = open(sys.argv[1])
    ehdr = Ehdr._from_file(ELFFILE)

    ELFFILE.seek(ehdr.phoff)
    phdr = Phdr._from_file(ELFFILE)

    ELFFILE.seek(ehdr.shoff)
    shdr = Shdr._from_file(ELFFILE)

    for i in range(ehdr.shnum):
        ELFFILE.seek(ehdr.shoff+i*ehdr.shentsize)
        shdr = Shdr._from_file(ELFFILE)
        print "%(name)08x %(flags)x %(addr)08x %(offset)08x" % shdr







