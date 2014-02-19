"""
Maps the BRL-CAD primitive type codes to the python wrapper classes.
"""
import warnings

import brlcad._bindings.librt as librt
from brlcad.exceptions import BRLCADException
from arb8 import ARB8
from base import Primitive
from arbn import ARBN
from ellipsoid import Ellipsoid, Sphere
from rpc import RPC, RHC
from tgc import TGC
from torus import Torus
from epa import EPA, EHY
from combination import Combination
from hyperboloid import Hyperboloid


MAGIC_TO_PRIMITIVE_TYPE = {
    # TODO: add proper wrappers for all primitives which have here "Primitive" as wrapper
    librt.ID_ARBN: ("ARBN", ARBN, librt.RT_ARBN_INTERNAL_MAGIC, librt.struct_rt_arbn_internal),
    librt.ID_ARB8: ("ARB", ARB8, librt.RT_ARB_INTERNAL_MAGIC, librt.struct_rt_arb_internal),
    librt.ID_ARS: ("ARS", Primitive, librt.RT_ARS_INTERNAL_MAGIC, librt.struct_rt_ars_internal),
    librt.ID_BINUNIF: ("BINUNIF", Primitive, librt.RT_BINUNIF_INTERNAL_MAGIC, librt.struct_rt_binunif_internal),
    librt.ID_BOT: ("BOT", Primitive, librt.RT_BOT_INTERNAL_MAGIC, librt.struct_rt_bot_internal),
    librt.ID_BREP: ("BREP", Primitive, librt.RT_BREP_INTERNAL_MAGIC, librt.struct_rt_brep_internal),
    librt.ID_CLINE: ("CLINE", Primitive, librt.RT_CLINE_INTERNAL_MAGIC, librt.struct_rt_cline_internal),
    librt.ID_DSP: ("DSP", Primitive, librt.RT_DSP_INTERNAL_MAGIC, librt.struct_rt_dsp_internal),
    librt.ID_EBM: ("EBM", Primitive, librt.RT_EBM_INTERNAL_MAGIC, librt.struct_rt_ebm_internal),
    librt.ID_EHY: ("EHY", EHY, librt.RT_EHY_INTERNAL_MAGIC, librt.struct_rt_ehy_internal),
    librt.ID_ELL: ("ELL", Ellipsoid, librt.RT_ELL_INTERNAL_MAGIC, librt.struct_rt_ell_internal),
    librt.ID_SPH: ("ELL", Sphere, librt.RT_ELL_INTERNAL_MAGIC, librt.struct_rt_ell_internal),
    librt.ID_EPA: ("EPA", EPA, librt.RT_EPA_INTERNAL_MAGIC, librt.struct_rt_epa_internal),
    librt.ID_ETO: ("ETO", Primitive, librt.RT_ETO_INTERNAL_MAGIC, librt.struct_rt_eto_internal),
    librt.ID_EXTRUDE: ("EXTRUDE", Primitive, librt.RT_EXTRUDE_INTERNAL_MAGIC, librt.struct_rt_extrude_internal),
    librt.ID_GRIP: ("GRIP", Primitive, librt.RT_GRIP_INTERNAL_MAGIC, librt.struct_rt_grip_internal),
    librt.ID_HALF: ("HALF", Primitive, librt.RT_HALF_INTERNAL_MAGIC, librt.struct_rt_half_internal),
    librt.ID_HF: ("HF", Primitive, librt.RT_HF_INTERNAL_MAGIC, librt.struct_rt_hf_internal),
    librt.ID_HYP: ("HYP", Hyperboloid, librt.RT_HYP_INTERNAL_MAGIC, librt.struct_rt_hyp_internal),
    librt.ID_METABALL: ("METABALL", Primitive, librt.RT_METABALL_INTERNAL_MAGIC, librt.struct_rt_metaball_internal),
    librt.ID_BSPLINE: ("NURB", Primitive, librt.RT_NURB_INTERNAL_MAGIC, librt.struct_rt_nurb_internal),
    librt.ID_POLY: ("PG", Primitive, librt.RT_PG_INTERNAL_MAGIC, librt.struct_rt_pg_internal),
    librt.ID_PIPE: ("PIPE", Primitive, librt.RT_PIPE_INTERNAL_MAGIC, librt.struct_rt_pipe_internal),
    librt.ID_PARTICLE: ("PARTICLE", Primitive, librt.RT_PART_INTERNAL_MAGIC, librt.struct_rt_part_internal),
    librt.ID_REVOLVE: ("REVOLVE", Primitive, librt.RT_REVOLVE_INTERNAL_MAGIC, librt.struct_rt_revolve_internal),
    librt.ID_RHC: ("RHC", RHC, librt.RT_RHC_INTERNAL_MAGIC, librt.struct_rt_rhc_internal),
    librt.ID_RPC: ("RPC", RPC, librt.RT_RPC_INTERNAL_MAGIC, librt.struct_rt_rpc_internal),
    librt.ID_SKETCH: ("SKETCH", Primitive, librt.RT_SKETCH_INTERNAL_MAGIC, librt.struct_rt_sketch_internal),
    librt.ID_SUBMODEL: ("SUBMODEL", Primitive, librt.RT_SUBMODEL_INTERNAL_MAGIC, librt.struct_rt_submodel_internal),
    librt.ID_SUPERELL: ("SUPERELL", Primitive, librt.RT_SUPERELL_INTERNAL_MAGIC, librt.struct_rt_superell_internal),
    librt.ID_TGC: ("TGC", TGC, librt.RT_TGC_INTERNAL_MAGIC, librt.struct_rt_tgc_internal),
    librt.ID_REC: ("REC", TGC, librt.RT_TGC_INTERNAL_MAGIC, librt.struct_rt_tgc_internal),
    librt.ID_TOR: ("TOR", Torus, librt.RT_TOR_INTERNAL_MAGIC, librt.struct_rt_tor_internal),
    librt.ID_VOL: ("VOL", Primitive, librt.RT_VOL_INTERNAL_MAGIC, librt.struct_rt_vol_internal),
    librt.ID_PNTS: ("PNTS", Primitive, librt.RT_PNTS_INTERNAL_MAGIC, librt.struct_rt_pnts_internal),
    librt.ID_ANNOTATION: ("ANNOTATION", Primitive, librt.RT_ANNOTATION_INTERNAL_MAGIC, librt.struct_rt_annotation_internal),
    librt.ID_HRT: ("HRT", Primitive, librt.RT_HRT_INTERNAL_MAGIC, librt.struct_rt_hrt_internal),
    librt.ID_COMBINATION: ("COMBINATION", Combination, librt.RT_COMB_MAGIC, librt.struct_rt_comb_internal),
    librt.ID_CONSTRAINT: ("CONSTRAINT", Primitive, librt.RT_CONSTRAINT_MAGIC, librt.struct_rt_constraint_internal),
}


def create_primitive(type_id, db_internal, directory):
    # TODO: research if this method won't cause a memory leak
    # because python will not free the structures received here
    name = str(directory.d_namep)
    type_info = MAGIC_TO_PRIMITIVE_TYPE.get(type_id)
    if type_info:
        magic = type_info[2]
        struct_type = type_info[3]
        data = struct_type.from_address(db_internal.idb_ptr) if struct_type else None
        # the first int32 is always the magic:
        data_magic = librt.cast(db_internal.idb_ptr, librt.POINTER(librt.c_uint32)).contents.value
        if magic:
            if magic != data_magic:
                raise BRLCADException("Invalid magic value, expected {0} but got {1}".format(magic, data_magic))
        else:
            if type_info[2]:
                display_type_info = list(type_info)
                display_type_info[2] = hex(display_type_info[2])
            else:
                display_type_info = type_info
            warnings.warn("No magic for type: {0}, {1}, {2}".format(type_id, hex(data_magic), display_type_info))
        if type_info[1] == Primitive:
            return Primitive(name=name, primitive_type=type_info[0], data=data)
        else:
            return type_info[1].from_wdb(name=name, data=data)
    else:
        return Primitive(name=name, primitive_type="UNKNOWN")

