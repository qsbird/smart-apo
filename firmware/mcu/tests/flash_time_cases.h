/* Stateful NOR/time fault cases shared by the native flash_nor executable. */
static void reset_time_case(void)
{
    memset(memory, 0xff, sizeof(memory));
    opcode=0; status=0; address=0; selected=0; pp_count=0;
    deny_wel=0; corrupt_write=0; read_fail=0;
    now_us=0; program_start=0; program_duration=0; tick_us=10;
    polls=0; time_calls=0; time_fail_call=0; time_fail=0; freeze_time=0;
    backwards_time=0; status_fail=0; tx_fail=0; cs_fail=0; fail_after_program=0;
}

static void flash_time_cases(void)
{
    uint8_t data[256], out[256];
    memset(data, 0xa5, sizeof(data));
    const uint32_t durations[] = {3000u, FLASH_BUSY_TIMEOUT_US-10u,
                                 FLASH_BUSY_TIMEOUT_US, FLASH_BUSY_TIMEOUT_US+10u};
    for (unsigned i=0; i<sizeof(durations)/sizeof(durations[0]); ++i) {
        reset_time_case(); program_duration=durations[i];
        int result=flash_page_program(0,data,sizeof(data));
        assert(result==(durations[i]<=FLASH_BUSY_TIMEOUT_US ? 0 : -1));
        assert(pp_count==1 && selected==0);
    }
    /* Natural UINT32 wrap remains a small positive elapsed interval. */
    reset_time_case(); now_us=UINT32_MAX-500u; program_duration=3000;
    assert(flash_page_program(0,data,sizeof(data))==0 && pp_count==1 && selected==0);
    /* A ready result sampled after the deadline must not become success. */
    reset_time_case(); tick_us=3000u;
    pp_count=1; program_duration=5000u;
    assert(flash_read(0,out,sizeof(out))==-1 && selected==0);
    reset_time_case(); time_fail=1;
    assert(flash_page_program(0,data,sizeof(data))==-1 && polls==1 && pp_count==0 && selected==0);
    reset_time_case(); time_fail=1;
    assert(flash_read(0,out,sizeof(out))==0 && selected==0);
    status=W25Q_SR1_BUSY;
    assert(flash_read(0,out,sizeof(out))==-1 && selected==0);
    reset_time_case(); backwards_time=1;
    assert(flash_page_program(0,data,sizeof(data))==-1 && pp_count==0 && selected==0);
    /* A bad mock returning success without progress cannot authorize a write. */
    reset_time_case(); freeze_time=1;
    assert(flash_page_program(0,data,sizeof(data))==-1 && pp_count==0 && selected==0);
    assert(polls==2);
    reset_time_case(); status=W25Q_SR1_BUSY; time_fail_call=2;
    assert(flash_read(0,out,sizeof(out))==-1 && polls==1 && selected==0);
    reset_time_case(); status=W25Q_SR1_BUSY; backwards_time=1;
    assert(flash_read(0,out,sizeof(out))==-1 && polls==2 && selected==0);
    reset_time_case(); freeze_time=1; status=W25Q_SR1_BUSY;
    assert(flash_read(0,out,sizeof(out))==-1 && polls==FLASH_BUSY_STALL_MAX && selected==0);
    reset_time_case(); status=W25Q_SR1_BUSY;
    assert(flash_read(0,out,sizeof(out))==-1 && now_us==FLASH_BUSY_TIMEOUT_US && selected==0);
    reset_time_case(); fail_after_program=1; program_duration=1000;
    assert(flash_page_program(0,data,sizeof(data))==-1 && pp_count==1 && selected==0);
    /* Lost confirmation never causes a hidden program retry. */
    time_fail=0; fail_after_program=0;
    assert(flash_page_program(0,data,sizeof(data))==0 && pp_count==1 && selected==0);
    reset_time_case(); status_fail=1;
    assert(flash_read(0,out,sizeof(out))==-1 && selected==0);
    reset_time_case(); tx_fail=1;
    assert(flash_read(0,out,sizeof(out))==-1 && selected==0);
    reset_time_case(); cs_fail=1;
    assert(flash_read(0,out,sizeof(out))==-1 && selected==0);
}
