#include "app.h"
#include "datalog.h"
#include <assert.h>
#include <string.h>
static int header_send_result, header_read_result, header_sends;
static datalog_header_t last_header;
static int init_result, append_result, flush_result, read_result, send_result;
static int clock_result, poll_result = 1, led_fault;
static uint32_t clock_now, clock_last;
static int clock_seen, clock_reads, stop_calls, uart_ready, uart_inits;
int board_time_us(uint32_t *n) {
    ++clock_reads;
    if(clock_result) return -1;
    if(clock_seen && clock_now-clock_last>INT32_MAX) {clock_result=-1; return -1;}
    clock_seen=1; clock_last=clock_now; *n=clock_now; return 0;
}
static int held, closed, polls, sends, reads, count, cursor;
static smart_apo_sample_t records[16], sent;
void board_enable_syscfg(void) {} void board_apply_pa9_pa10_remap(void) {}
int board_start_clocks(void) {clock_seen=0; return 0;}
void board_init_gpio(void) {} void board_spi1_init(void) {} void board_i2c1_init(void) {}
void board_reed_exti_setup(void) {} void board_imu_int_exti_setup(void) {}
void board_usart2_init(void) {uart_ready=1; ++uart_inits;} void board_buses_reinit_after_stop(void) {++stop_calls; clock_result=-1;}
int board_reed_is_closed(void) {return closed;}
int board_reed_held_for_sleep(void) {return held;}
int datalog_init(uint32_t h) {(void)h; count=cursor=0; return init_result;}
int datalog_flush_page(void) {return flush_result;}
int datalog_append(const smart_apo_sample_t *s) {
    if(append_result) return -1;
    assert(count<16); records[count++]=*s; return 0;
}
int datalog_dump_begin(void) {cursor=0; return init_result<0?-1:0;}
int datalog_dump_header(datalog_header_t *h) {
    if(header_read_result) return -1;
    *h=(datalog_header_t){.magic=DATALOG_MAGIC,.variant=SMART_APO_VARIANT};return 0;
}
int uart_dump_send_header(const datalog_header_t *h) {
    last_header=*h;++header_sends;return header_send_result;
}
int datalog_dump_next(smart_apo_sample_t *s) {
    ++reads; if(read_result) return -1;
    if(cursor==count) return 0;
    *s=records[cursor++]; return 1;
}
int led_output_failed(void) {return led_fault;}
void led_init(void) {} void led_cancel(void) {} void led_poll(uint32_t n) {(void)n;}
void sensors_init(sensors_status_t *s) {memset(s,0,sizeof(*s));}
int sensors_poll(uint32_t n, smart_apo_sample_t *s, const sensors_status_t *st) {
    (void)st; ++polls; memset(s,0,sizeof(*s)); s->timestamp_us=n; return poll_result;
}
int uart_dump_send_sample(const smart_apo_sample_t *s) {
    sent=*s; ++sends;
    if (!uart_ready) return -1;
    if (send_result) {uart_ready=0; return -1;} /* real backend latches faults */
    return 0;
}
int main(void) {
    sensors_status_t st; app_state_t state;
    init_result=-1; state=app_boot(&st); assert(state==APP_ERROR);
    assert(app_error_flags()&APP_ERROR_LOG_INIT);
    assert(app_step(state,0,&st)==APP_ERROR && polls==0);
    init_result=0; state=app_boot(&st); assert(state==APP_RECORD);
    state=app_step(state,1000,&st);
    assert(!(records[0].flags&SAMPLE_FLAG_SYNC_TAP));
    held=1; state=app_step(state,2000,&st); assert(state==APP_DUMP && count==2);
    int uart_before=uart_inits; send_result=-1;
    state=app_step(state,3000,&st); assert(state==APP_DUMP && sends==1 && reads==1 && sent.sequence==0);
    state=app_step(state,4000,&st); assert(state==APP_DUMP && sends==2 && reads==1 && sent.sequence==0);
    assert(uart_inits==uart_before+2);
    send_result=0;
    state=app_step(state,5000,&st); assert(state==APP_DUMP && sends==3 && reads==1);
    state=app_step(state,6000,&st); assert(state==APP_DUMP && sent.sequence==1);
    state=app_step(state,7000,&st); assert(state==APP_SLEEP);
    assert(app_error_flags()&APP_ERROR_UART);
    held=0; state=app_boot(&st); append_result=-1;
    state=app_step(state,1000,&st); assert(state==APP_ERROR);
    assert(app_error_flags()&APP_ERROR_LOG_APPEND);
    int old_polls=polls; assert(app_step(state,2000,&st)==APP_ERROR && polls==old_polls);
    held=1; state=app_step(state,3000,&st); assert(state==APP_DUMP);
    state=app_step(state,4000,&st); assert(state==APP_DUMP && sent.timestamp_us==1000);
    state=app_step(state,5000,&st); assert(state==APP_SLEEP);
    closed=1; state=app_step(state,6000,&st); assert(state==APP_DUMP); /* cannot resume unsafe writes */
    state=app_step(state,7000,&st); assert(state==APP_DUMP && sent.timestamp_us==1000); /* retry entire dump */
    closed=0; append_result=0; state=app_boot(&st); flush_result=-1;
    state=app_step(state,1000,&st); assert(state==APP_DUMP);
    assert(app_error_flags()&APP_ERROR_LOG_FLUSH);
    read_result=-1; state=app_step(state,2000,&st); assert(state==APP_ERROR);
    assert(app_error_flags()&APP_ERROR_LOG_READ);
    read_result=0; flush_result=0; init_result=1; state=app_boot(&st); assert(state==APP_DUMP);
    state=app_step(state,1000,&st); assert(state==APP_SLEEP);
    closed=1; state=app_step(state,2000,&st); assert(state==APP_DUMP); /* historical log stays read-only */
    held=closed=init_result=0; state=app_boot(&st);
    clock_result=-1; int before=polls;
    state=app_step_from_clock(state,&st);
    assert(state==APP_ERROR && polls==before && count==0);
    assert(app_error_flags()&APP_ERROR_CLOCK);
    held=0; closed=1; state=app_step_from_clock(state,&st); assert(state==APP_DUMP);
    closed=0; state=app_step_from_clock(state,&st); assert(state==APP_SLEEP);
    closed=1; state=app_step_from_clock(state,&st); assert(state==APP_DUMP);
    held=closed=0; state=app_boot(&st); clock_result=0; clock_now=12345;
    state=app_step_from_clock(state,&st);
    assert(state==APP_RECORD && count==1 && records[0].timestamp_us==12345);
    poll_result=-1; state=app_step_from_clock(state,&st);
    assert(state==APP_ERROR && count==1 && (app_error_flags()&APP_ERROR_CLOCK));
    /* Software idle must keep the live epoch, including hours and wrap. */
    held=closed=init_result=append_result=flush_result=read_result=send_result=clock_result=0;
    poll_result=1; clock_now=100; stop_calls=0;
    state=app_boot(&st);
    state=app_step_from_clock(state,&st); assert(state==APP_RECORD);
    held=1; closed=1; clock_now=200;
    state=app_step_from_clock(state,&st); assert(state==APP_DUMP);
    held=closed=0; send_result=-1;
    int dump_count=count;
    for(unsigned j=0;j<16;++j) {
        clock_now+=900000000u;
        state=app_step_from_clock(state,&st);
        assert(state==APP_DUMP && count==dump_count);
        assert(!(app_error_flags()&APP_ERROR_CLOCK));
    }
    send_result=0;
    while(state==APP_DUMP) {++clock_now; state=app_step_from_clock(state,&st);}
    assert(state==APP_SLEEP);
    int idle_count=count, idle_polls=polls, serviced=clock_reads;
    for(unsigned j=0;j<16;++j) {
        clock_now+=900000000u; /* 15-minute servicing, four hours total */
        state=app_step_from_clock(state,&st);
        assert(state==APP_SLEEP && count==idle_count && polls==idle_polls);
    }
    assert(clock_reads==serviced+16 && clock_result==0);
    closed=1; ++clock_now; state=app_step_from_clock(state,&st);
    assert(state==APP_RECORD && stop_calls==0);
    ++clock_now; state=app_step_from_clock(state,&st);
    assert(state==APP_RECORD && records[count-1].timestamp_us==clock_now);
    assert(!(app_error_flags()&APP_ERROR_CLOCK));
    /* Clock loss in software idle cannot lead back to recording. */
    clock_result=-1; held=0; closed=0;
    state=app_step_from_clock(APP_SLEEP,&st);
    assert(state==APP_SLEEP && (app_error_flags()&APP_ERROR_CLOCK));
    closed=1; state=app_step_from_clock(state,&st);
    assert(state==APP_DUMP); /* Read-only recovery without a timed hold. */
    state=app_step_from_clock(APP_ERROR,&st);
    assert(state==APP_DUMP && stop_calls==0);
    led_fault=1; assert(app_error_flags()&APP_ERROR_LED);
    led_fault=0; assert(app_error_flags()&APP_ERROR_LED); /* sticky */
    /* A failed metadata frame must be retried before consuming sample 0. */
    init_result=held=closed=append_result=flush_result=read_result=send_result=clock_result=0;
    poll_result=1;state=app_boot(&st);state=app_step(state,10,&st);
    held=1;state=app_step(state,20,&st);assert(state==APP_DUMP);
    int old_reads=reads, old_sends=sends, old_headers=header_sends;
    header_send_result=-1;state=app_step(state,30,&st);
    assert(state==APP_DUMP && reads==old_reads && sends==old_sends && header_sends==old_headers+1);
    datalog_header_t first_header=last_header;
    state=app_step(state,40,&st);assert(memcmp(&first_header,&last_header,sizeof(first_header))==0);
    assert(reads==old_reads && sends==old_sends);
    header_send_result=0;state=app_step(state,50,&st);
    assert(state==APP_DUMP && sent.sequence==0 && reads==old_reads+1);
    state=app_step(APP_ERROR,60,&st);assert(state==APP_DUMP);
    header_read_result=-1;old_reads=reads;state=app_step(state,70,&st);
    assert(state==APP_ERROR && reads==old_reads && (app_error_flags()&APP_ERROR_LOG_READ));
    return 0;
}
