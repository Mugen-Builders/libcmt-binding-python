from libc.stdint cimport uint64_t, uint8_t
from libc.stdlib cimport free, malloc
cimport libcmt

cdef class Rollup:
    cdef libcmt.cmt_rollup_t _c_rollup[1]
    cdef libcmt.cmt_abi_address_t *app_address

    def __cinit__(self):
        libcmt.cmt_rollup_init(self._c_rollup)

    def __dealloc__(self):
        libcmt.cmt_rollup_fini(self._c_rollup)

    cpdef str finish(self, bint last_request_status):
        cdef libcmt.cmt_rollup_finish_t finish[1]
        finish[0].accept_previous_request = last_request_status
        err = libcmt.cmt_rollup_finish(self._c_rollup, finish)
        if err != 0:
            raise Exception(f"Failed to finish rollup ({err})")
        if finish[0].next_request_type == libcmt.HTIF_YIELD_REASON_ADVANCE:
            return "advance"
        if finish[0].next_request_type == libcmt.HTIF_YIELD_REASON_INSPECT:
            return "inspect"
        raise Exception(f"Unknown next request type ({finish[0].next_request_type})")

    cpdef object read_advance_state(self):
        cdef libcmt.cmt_rollup_advance_t input[1]
        err = libcmt.cmt_rollup_read_advance_state(self._c_rollup, input)
        if err != 0:
            raise Exception(f"Failed to read advance ({err})")
        self.app_address = &input[0].app_contract
        payload = input[0].payload.data[:input[0].payload.length]
        app_contract = input[0].app_contract.data[:libcmt.CMT_ABI_ADDRESS_LENGTH]
        msg_sender = input[0].msg_sender.data[:libcmt.CMT_ABI_ADDRESS_LENGTH]
        prev_randao = input[0].prev_randao.data[:libcmt.CMT_ABI_U256_LENGTH]
        ret = dict(input[0])
        ret['payload']['data'] = payload
        ret['app_contract'] = app_contract
        ret['msg_sender'] = msg_sender
        ret['prev_randao'] = prev_randao
        return ret

    cpdef object read_inspect_state(self):
        cdef libcmt.cmt_rollup_inspect_t input[1]
        err = libcmt.cmt_rollup_read_inspect_state(self._c_rollup, input)
        if err != 0:
            raise Exception(f"Failed to read inspect ({err})")
        payload = input[0].payload.data[:input[0].payload.length]
        ret = dict(input[0])
        ret['payload']['data'] = payload
        return ret

    cpdef int emit_voucher(self, str address, object value, bytes payload):
        if address.startswith("0x"):
            address = address[2:]
        cdef libcmt.cmt_abi_address_t address_ptr[1]
        address_ptr[0].data = bytes.fromhex(address[:(2*libcmt.CMT_ABI_ADDRESS_LENGTH)])[:libcmt.CMT_ABI_ADDRESS_LENGTH]
        cdef libcmt.cmt_abi_u256_t value_ptr[1]
        value_ptr[0].data = bytes.fromhex(f"{value:064x}")[:libcmt.CMT_ABI_U256_LENGTH]
        cdef libcmt.cmt_abi_bytes_t payload_ptr[1]
        payload_ptr[0].data = payload
        payload_ptr[0].length = len(payload)
        cdef uint64_t cindex[1]
        err = libcmt.cmt_rollup_emit_voucher(self._c_rollup, address_ptr, value_ptr, payload_ptr, cindex)
        if err != 0:
            raise Exception(f"Failed to emit voucher ({err})")
        return cindex[0]

    cpdef int emit_delegate_call_voucher(self, str address, bytes payload):
        if address.startswith("0x"):
            address = address[2:]
        cdef libcmt.cmt_abi_address_t address_ptr[1]
        address_ptr[0].data = bytes.fromhex(address[:(2*libcmt.CMT_ABI_ADDRESS_LENGTH)])[:libcmt.CMT_ABI_ADDRESS_LENGTH]
        cdef libcmt.cmt_abi_bytes_t payload_ptr[1]
        payload_ptr[0].data = payload
        payload_ptr[0].length = len(payload)
        cdef uint64_t cindex[1]
        err = libcmt.cmt_rollup_emit_delegate_call_voucher(self._c_rollup, address_ptr, payload_ptr, cindex)
        if err != 0:
            raise Exception(f"Failed to emit delegate call voucher ({err})")
        return cindex[0]

    cpdef int emit_notice(self, bytes payload):
        cdef libcmt.cmt_abi_bytes_t payload_ptr[1]
        payload_ptr[0].data = payload
        payload_ptr[0].length = len(payload)
        cdef uint64_t cindex[1]
        err = libcmt.cmt_rollup_emit_notice(self._c_rollup, payload_ptr, cindex)
        if err != 0:
            raise Exception(f"Failed to emit notice ({err})")
        return cindex[0]

    cpdef emit_report(self, bytes payload):
        cdef libcmt.cmt_abi_bytes_t payload_ptr[1]
        payload_ptr[0].data = payload
        payload_ptr[0].length = len(payload)
        err = libcmt.cmt_rollup_emit_report(self._c_rollup, payload_ptr)
        if err != 0:
            raise Exception(f"Failed to emit report ({err})")

    cpdef emit_exception(self, bytes payload):
        cdef libcmt.cmt_abi_bytes_t payload_ptr[1]
        payload_ptr[0].data = payload
        payload_ptr[0].length = len(payload)
        err = libcmt.cmt_rollup_emit_exception(self._c_rollup, payload_ptr)
        if err != 0:
            raise Exception(f"Failed to emit exception ({err})")
