#include <core.p4>
#include <v1model.p4>
#include "CONSTANTS.p4"
#include "headers.p4"
#include "parser.p4"


#ifndef RECIRCULATION_AND_CLONE_CONTROL_LOGIC
#define RECIRCULATION_AND_CLONE_CONTROL_LOGIC
control recirculation_and_clone_control_logic(inout parsed_headers_t    hdr,
                        inout local_metadata_t    local_metadata,
                        inout standard_metadata_t standard_metadata)
{


   action send_to_cpu() {
       standard_metadata.egress_spec = CPU_PORT;
   }

   action clone_to_cpu() {
       // Cloning is achieved by using a v1model-specific primitive. Here we
       // set the type of clone operation (ingress-to-egress pipeline), the
       // clone session ID (the CPU one), and the metadata fields we want to
       // preserve for the cloned packet replica.
       clone3(CloneType.I2E, CPU_CLONE_SESSION_ID, { standard_metadata.ingress_port });
   }

   table acl_table {
       key = {
           local_metadata.flag_hdr.is_control_pkt_from_egr_queue_depth: exact;
           local_metadata.flag_hdr.is_control_pkt_from_egr_queue_rate: exact;
       }
       actions = {
           send_to_cpu;
           clone_to_cpu;
           drop;
           NoAction;
       }
       const default_action = NoAction;

       @name("acl_table_counter")
       counters = direct_counter(CounterType.packets_and_bytes);
   }
   apply {
        acl_table.apply();
   }
}
#endif




