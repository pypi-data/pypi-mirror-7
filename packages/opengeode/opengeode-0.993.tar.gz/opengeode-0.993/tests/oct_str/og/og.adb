-- This file was generated automatically: DO NOT MODIFY IT !

with System.IO;
use System.IO;

with TASTE_Dataview;
use TASTE_Dataview;

with adaasn1rtl;
use adaasn1rtl;

with Interfaces;
use Interfaces;

package body og is
    l_MSG : aliased asn1SccMy_OctStr;
    l_test : aliased asn1SccSome_Thing;
    l_first_msg : aliased asn1SccMy_OctStr;
    l_seq : aliased asn1SccSeqOf;
    type states is (START, running, wait);
    state : states := START;
    function get_state return String;
    pragma export(C, get_state, "og_state");
    procedure runTransition(trId: Integer);
    procedure Go(ze_param: access asn1SccMy_OctStr) is
        begin
            case state is
                when running =>
                    l_msg := ze_param.all;
                    runTransition(1);
                when wait =>
                    l_msg := ze_param.all;
                    runTransition(2);
                when others =>
                    null;
            end case;
        end Go;
        

    procedure runTransition(trId: Integer) is
        tmp6 : aliased asn1SccSeqOf;
        tmp5 : aliased asn1SccSeqOf;
        tmp8 : aliased asn1SccSeqOf;
        tmp11 : aliased asn1SccSeqOf;
        tmp15 : aliased asn1SccSeqOf;
        tmp17 : aliased asn1SccSeqOf;
        tmp21 : BOOLEAN := False;
        tmp31 : BOOLEAN := False;
        tmp38 : aliased asn1SccMy_OctStr;
        tmp42 : aliased asn1SccMy_OctStr;
        tmp45 : aliased asn1SccMy_OctStr;
        tmp48 : aliased asn1SccMy_OctStr;
        tmp47 : aliased asn1SccMy_OctStr;
        tmp51 : aliased asn1SccMy_OctStr;
        tmp55 : aliased asn1SccMy_OctStr;
        tmp57 : aliased asn1SccMy_OctStr;
        tmp60 : aliased asn1SccMy_OctStr;
        tmp63 : aliased asn1SccMy_OctStr;
        tmp70 : aliased asn1SccMy_OctStr;
        tmp73 : aliased asn1SccMy_OctStr;
        begin
            case trId is
                when 0 =>
                    -- ASSIGN: test := 5 (16,5)
                    l_test := 5;
                    -- COMMENT String assignment (20,0)
                    -- ASSIGN: first_msg := 'Say hello first!' (18,5)
                    l_first_msg := (Data => (83, 97, 121, 32, 104, 101, 108, 108, 111, 32, 102, 105, 114, 115, 116, 33, others => 0), Length => 16);
                    -- COMMENT default_seqof is a constant
                    -- defined in the ASN.1 model (25,0)
                    -- ASSIGN: seq := default_seqof (22,5)
                    l_seq := default_seqof;
                    -- ASSIGN: seq := {1,2,3} (23,0)
                    l_seq := asn1SccSeqOf'(Length => 3, Data => asn1SccSeqOf_array'(1 => 1, 2 => 2, 3 => 3, others => 3));
                    -- COMMENT Concatenate
                    -- two SEQUENCE OF (30,0)
                    -- ASSIGN: seq := seq // {4, test} // default_seqof (28,5)
                    tmp5 := asn1SccSeqOf'(Length => 2, Data => asn1SccSeqOf_array'(1 => 4, 2 => l_test, others => l_test));
                    tmp6.Data(1..l_seq.Length) := l_seq.Data(1..l_seq.Length);
                    tmp6.Data(l_seq.Length+1..l_seq.Length+2) := tmp5.Data(1..2);
                    tmp6.Length := l_seq.Length + 2;
                    tmp8.Data(1..tmp6.Length) := tmp6.Data(1..tmp6.Length);
                    tmp8.Data(tmp6.Length+1..tmp6.Length+default_seqof.Length) := default_seqof.Data(1..default_seqof.Length);
                    tmp8.Length := tmp6.Length + default_seqof.Length;
                    l_seq := tmp8;
                    --  seq(1) := seq(2)
                    -- COMMENT Remove 3rd element (37,0)
                    -- ASSIGN: seq := seq(1,2) // seq(4,5) (35,5)
                    tmp11.Length := 2;
                    tmp11.Data(1..2) := l_seq.Data(1..2);
                    tmp15.Length := 2;
                    tmp15.Data(1..2) := l_seq.Data(4..5);
                    tmp17.Data(1..tmp11.Length) := tmp11.Data(1..tmp11.Length);
                    tmp17.Data(tmp11.Length+1..tmp11.Length+tmp15.Length) := tmp15.Data(1..tmp15.Length);
                    tmp17.Length := tmp11.Length + tmp15.Length;
                    l_seq := tmp17;
                    -- DECISION test in seq (39,14)
                    -- COMMENT Test the "in" operator (41,0)
                    in_loop_tmp21:
                    for elem in 1..Integer(l_seq.Length) loop
                        if l_seq.Data(elem) = l_test then
                            tmp21 := True;
                        end if;
                        exit in_loop_tmp21 when tmp21 = True;
                    end loop in_loop_tmp21;
                    if tmp21 = false then
                        -- PROCEDURE_CALL writeln('NOT OK (1)') (45,5)
                        Put_Line("NOT OK (1)");
                    elsif tmp21 = true then
                        -- PROCEDURE_CALL writeln('All OK (1)') (49,5)
                        Put_Line("All OK (1)");
                    end if;
                    -- DECISION 3 in seq (52,11)
                    in_loop_tmp31:
                    for elem in 1..Integer(l_seq.Length) loop
                        if l_seq.Data(elem) = 3 then
                            tmp31 := True;
                        end if;
                        exit in_loop_tmp31 when tmp31 = True;
                    end loop in_loop_tmp31;
                    if tmp31 = false then
                        -- PROCEDURE_CALL writeln('All OK (2)') (56,5)
                        Put_Line("All OK (2)");
                    elsif tmp31 = true then
                        -- PROCEDURE_CALL writeln('NOT OK (2)') (60,5)
                        Put_Line("NOT OK (2)");
                    end if;
                    -- NEXT_STATE Wait (63,10) at -252, 751
                    state := Wait;
                    return;
                when 1 =>
                    -- DECISION msg (72,9)
                    -- COMMENT Switch-case
                    -- on strings (74,0)
                    tmp38 := l_msg;
                    if asn1SccMy_OctStr_Equal(tmp38, (Data => (101, 110, 100, others => 0), Length => 3)) then
                        -- OUTPUT rezult
                        -- ('Goodbye!') (79,7)
                        tmp42 := (Data => (71, 111, 111, 100, 98, 121, 101, 33, others => 0), Length => 8);
                        rezult(tmp42'access);
                        -- NEXT_STATE Wait (82,10) at 94, 353
                        state := Wait;
                        return;
                    elsif asn1SccMy_OctStr_Equal(tmp38, (Data => (101, 103, 103, others => 0), Length => 3)) then
                        -- OUTPUT rezult(default_str) (86,7)
                        -- COMMENT Send a constant
                        -- defined in the ASN.1
                        -- model (88,0)
                        tmp45 := default_str;
                        rezult(tmp45'access);
                        -- NEXT_STATE Running (92,10) at 670, 351
                        state := Running;
                        return;
                    else
                        -- COMMENT Concatenate
                        -- strings (98,0)
                        -- ASSIGN: msg := msg // '!' (96,5)
                        tmp47 := (Data => (33, others => 0), Length => 1);
                        tmp48.Data(1..l_msg.Length) := l_msg.Data(1..l_msg.Length);
                        tmp48.Data(l_msg.Length+1..l_msg.Length+1) := tmp47.Data(1..1);
                        tmp48.Length := l_msg.Length + 1;
                        l_msg := tmp48;
                        -- COMMENT Concatenate two substrings
                        -- (can be used to remove an
                        -- element from a list) (103,0)
                        -- ASSIGN: msg := msg(3,4) // msg(1,2) (101,5)
                        tmp51.Length := 2;
                        tmp51.Data(1..2) := l_msg.Data(3..4);
                        tmp55.Length := 2;
                        tmp55.Data(1..2) := l_msg.Data(1..2);
                        tmp57.Data(1..tmp51.Length) := tmp51.Data(1..tmp51.Length);
                        tmp57.Data(tmp51.Length+1..tmp51.Length+tmp55.Length) := tmp55.Data(1..tmp55.Length);
                        tmp57.Length := tmp51.Length + tmp55.Length;
                        l_msg := tmp57;
                        -- COMMENT Substring
                        -- TODO check range
                        -- against current Length (109,0)
                        -- ASSIGN: msg := first_msg(1, 2) (107,5)
                        tmp60.Length := 2;
                        tmp60.Data(1..2) := l_first_msg.Data(1..2);
                        l_msg := tmp60;
                        -- OUTPUT rezult(msg) (113,7)
                        tmp63 := l_msg;
                        rezult(tmp63'access);
                        -- NEXT_STATE Running (115,10) at 258, 546
                        state := Running;
                        return;
                    end if;
                when 2 =>
                    -- DECISION msg = 'hello' (125,13)
                    -- COMMENT Boolean test
                    -- on string value (127,0)
                    if (l_msg = (Data => (104, 101, 108, 108, 111, others => 0), Length => 5)) = true then
                        -- OUTPUT rezult('Welcome') (132,7)
                        -- COMMENT Send raw
                        -- string (134,0)
                        tmp70 := (Data => (87, 101, 108, 99, 111, 109, 101, others => 0), Length => 7);
                        rezult(tmp70'access);
                        -- NEXT_STATE Running (137,10) at -312, 1091
                        state := Running;
                        return;
                    elsif (l_msg = (Data => (104, 101, 108, 108, 111, others => 0), Length => 5)) = false then
                        -- OUTPUT rezult(first_msg) (141,7)
                        tmp73 := l_first_msg;
                        rezult(tmp73'access);
                        -- NEXT_STATE Wait (143,10) at -41, 1091
                        state := Wait;
                        return;
                    end if;
                when others =>
                    null;
            end case;
        end runTransition;
        

    function get_state return String is
        begin
            return states'Image(state);
        end get_state;
        

    begin
        runTransition(0);
end og;