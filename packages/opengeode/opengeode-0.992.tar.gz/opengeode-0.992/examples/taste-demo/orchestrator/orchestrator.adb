-- This file was generated automatically: DO NOT MODIFY IT !

with System.IO;
use System.IO;

with TASTE_Dataview;
use TASTE_Dataview;

with adaasn1rtl;
use adaasn1rtl;

with Interfaces;
use Interfaces;

package body orchestrator is
    l_a : aliased asn1SccMyInteger;
    l_c : aliased asn1SccMySeq;
    l_b : aliased asn1SccMySeqOf;
    l_e : aliased asn1SccMyChoice;
    l_g : aliased asn1SccMyChoice;
    l_f : aliased asn1SccMyEnum;
    l_i : aliased asn1SccMyPossiblyEmptySeqOf;
    l_h : aliased asn1SccMyReal;
    l_k : aliased asn1SccMyComplexSeqOf;
    l_j : aliased asn1SccMyComplexType;
    l_toto : aliased asn1SccMySeqOf;
    l_l : aliased asn1SccMyComplexChoice;
    l_deep : aliased asn1SccDeepSeq;
    l_myCmd : aliased asn1SccMyInteger;
    type states is (START, running, stopped);
    state : states := START;
    procedure runTransition(trId: Integer);
    procedure myproc(l_toto: in asn1SccMyInteger;l_tutu: in out asn1SccMyInteger);
    procedure myproc(l_toto: in asn1SccMyInteger;l_tutu: in out asn1SccMyInteger) is
        l_foo : asn1SccMyInteger;
        tmp1 : aliased asn1SccMyInteger;
        begin
            -- ASSIGN: a := 42 (72,5)
            l_a := 42;
            -- DECISION toto (74,9)
            tmp1 := l_toto;
            if tmp1 < 10 then
                -- ASSIGN: tutu := 128 (78,5)
                l_tutu := 128;
            else
                -- ASSIGN: tutu := 254 (82,5)
                l_tutu := 254;
            end if;
            -- ASSIGN: foo := a (85,5)
            l_foo := l_a;
            -- STOP Wait (None,None) at 642, 351
        end myproc;
        

    procedure pulse is
        begin
            case state is
                when running =>
                    runTransition(4);
                when stopped =>
                    runTransition(3);
                when others =>
                    null;
            end case;
        end pulse;
        

    procedure run(cmd: access asn1SccMyInteger) is
        begin
            case state is
                when running =>
                    l_myCmd := cmd.all;
                    runTransition(1);
                when stopped =>
                    l_a := cmd.all;
                    runTransition(2);
                when others =>
                    null;
            end case;
        end run;
        

    procedure runTransition(trId: Integer) is
        tmp45 : asn1SccMyInteger;
        tmp43 : asn1SccMyInteger;
        tmp63 : asn1SccMyInteger;
        tmp80 : aliased asn1SccMyChoice;
        tmp116 : aliased asn1SccMyInteger;
        tmp127 : aliased asn1SccMyInteger;
        tmp130 : aliased asn1SccMyInteger;
        tmp91 : aliased asn1SccMyInteger;
        begin
            case trId is
                when 0 =>
                    -- COMMENT This is a multiline
                    -- comment - should
                    -- we reflected as so
                    -- in the generated code (122,0)
                    -- ASSIGN: a := 42 + 5 * 3 - 1 (92,5)
                    l_a := ((42 + (5 * 3)) - 1);
                    -- ASSIGN: b := { hello, world } (93,0)
                    l_b := asn1SccMySeqOf'(Data => asn1SccMySeqOf_array'(1 => asn1Scchello, 2 => asn1Sccworld, others => asn1Sccworld));
                    -- ASSIGN: a := length(b) (94,0)
                    l_a := 2;
                    -- ASSIGN: c := {a 5, b taste} (95,0)
                    l_c := asn1SccMySeq'(a => 5, b => asn1Scctaste);
                    -- ASSIGN: f := hello (96,0)
                    l_f := asn1Scchello;
                    -- ASSIGN: g := b:{a 33, b you} (97,0)
                    l_g := asn1SccMyChoice_b_set(asn1SccMySeq'(a => 33, b => asn1Sccyou));
                    -- ASSIGN: e:=g (98,0)
                    l_e := l_g;
                    -- ASSIGN: e := a:TRUE (99,0)
                    l_e := asn1SccMyChoice_a_set(true);
                    -- ASSIGN: b(0) := hello (100,0)
                    l_b.Data(1) := asn1Scchello;
                    -- ASSIGN: h := 42.5 (102,0)
                    l_h := 42.5;
                    -- ASSIGN: i := {} (103,0)
                    l_i := asn1SccMyPossiblyEmptySeqOf_Init;
                    -- ASSIGN: i := { 1 } (104,0)
                    l_i := asn1SccMyPossiblyEmptySeqOf'(Length => 1, Data => asn1SccMyPossiblyEmptySeqOf_array'(1 => 1, others => 1));
                    -- ASSIGN: a := length(i) (105,0)
                    l_a := Interfaces.Integer_64(l_i.Length);
                    -- ASSIGN: a := if e!a then 8 else  if b(0) = hello then a  else 9 fi fi (106,0)
                    if (l_b.Data(1) = asn1Scchello) then
                        tmp43 := l_a;
                    else
                        tmp43 := 9;
                    end if;
                    if asn1SccMyChoice_a_get(l_e) then
                        tmp45 := 8;
                    else
                        tmp45 := tmp43;
                    end if;
                    l_a := tmp45;
                    -- ASSIGN: j := { a { x 5, y 6 } } (107,0)
                    l_j := asn1SccMyComplexType'(a => asn1SccMyComplexType_a'(y => 6, x => 5));
                    -- ASSIGN: k := { {x 4}, {x 5} } (108,0)
                    l_k := asn1SccMyComplexSeqOf'(Data => asn1SccMyComplexSeqOf_array'(1 => asn1SccMyComplexSeqOf_elm'(x => 4), 2 => asn1SccMyComplexSeqOf_elm'(x => 5), others => asn1SccMyComplexSeqOf_elm'(x => 5)));
                    -- ASSIGN: l := a:{ x 5 } (109,0)
                    l_l := asn1SccMyComplexChoice_a_set(asn1SccMyComplexChoice_a'(x => 5));
                    -- ASSIGN: a:= if present(e)=b then 42 else 43 fi (110,0)
                    if (asn1SccMyChoice_Kind(l_e) = b_PRESENT) then
                        tmp63 := 42;
                    else
                        tmp63 := 43;
                    end if;
                    l_a := tmp63;
                    -- ASSIGN: deep!a!b!c := 3 (111,0)
                    l_deep.a.b.c := 3;
                    -- ASSIGN: deep!a := { b { c 4, d e:TRUE } } (112,0)
                    l_deep.a := asn1SccDeepSeq_a'(b => asn1SccDeepSeq_a_b'(c => 4, d => asn1SccDeepSeq_a_b_d_e_set(true)));
                    -- ASSIGN: deep!a!b!d := e:FALSE (119,0)
                    l_deep.a.b.d := asn1SccDeepSeq_a_b_d_e_set(false);
                    -- DECISION present(e) (127,9)
                    if asn1SccMyChoice_Kind(l_e) = b_PRESENT then
                        -- ASSIGN: a := 38 (131,5)
                        l_a := 38;
                    elsif asn1SccMyChoice_Kind(l_e) = MyChoice_a_PRESENT then
                        -- ASSIGN: a := 37 (135,5)
                        l_a := 37;
                    end if;
                    -- DECISION e (140,9)
                    tmp80 := l_e;
                    if asn1SccMyChoice_Equal(tmp80, l_g) then
                        -- ASSIGN: a := 40 (144,5)
                        l_a := 40;
                    elsif asn1SccMyChoice_Equal(tmp80, asn1SccMyChoice_a_set(true)) then
                        -- ASSIGN: a := 41 (148,5)
                        l_a := 41;
                    else
                        -- ASSIGN: a := 42 (152,5)
                        l_a := 42;
                    end if;
                    -- NEXT_STATE Stopped (155,10) at 615, 260
                    state := Stopped;
                    return;
                when 1 =>
                    -- PROCEDURE_CALL writeln
                    -- ('Already running! So stopping') (173,5)
                    Put_Line("Already running! So stopping");
                    -- JOIN Transition_to_Stop (176,5) at 16, 111
                    goto Transition_to_Stop;
                when 2 =>
                    goto Here;
                when 3 =>
                    -- OUTPUT housekeeping (1) (211,7)
                    tmp116 := 1;
                    housekeeping(tmp116'access);
                    -- NEXT_STATE - (213,10) at -532, -486
                    -- COMMENT Stay in the same state (215,0)
                    return;
                when 4 =>
                    -- ASSIGN: a := (a+1) mod 10 (223,5)
                    l_a := ((l_a + 1) mod 10);
                    -- PROCEDURE_CALL writeln
                    -- ('Calling GNC') (225,5)
                    Put_Line("Calling GNC");
                    -- PROCEDURE_CALL computeGNC(a, a) (228,5)
                    tmp127 := l_a;
                    computeGNC(tmp127'access, l_a'access);
                    -- OUTPUT housekeeping(a) (230,7)
                    tmp130 := l_a;
                    housekeeping(tmp130'access);
                    -- NEXT_STATE Running (232,10) at 272, -218
                    state := Running;
                    return;
                when others =>
                    null;
            end case;
            -- CONNECTION Transition_to_Stop (157,11)
            <<Transition_to_Stop>>
            -- PROCEDURE_CALL writeln
            -- ('Floating label: Transition to stop (Sending HK 31)') (159,5)
            Put_Line("Floating label: Transition to stop (Sending HK 31)");
            -- OUTPUT housekeeping(31) (162,7)
            tmp91 := 31;
            housekeeping(tmp91'access);
            -- NEXT_STATE Stopped (164,10) at -428, 3
            state := Stopped;
            return;
            -- LABEL Here (186,0)
            <<Here>>
            -- DECISION a>10 (188,10)
            if (l_a > 10) = true then
                -- PROCEDURE_CALL writeln
                -- ('a is too big! - decrementing :', a, a - 1) (194,5)
                Put("a is too big! - decrementing :");
                Put(Interfaces.Integer_64'Image(l_a));
                Put_Line(Interfaces.Integer_64'Image((l_a - 1)));
                -- ASSIGN: a := a - 1 (197,5)
                l_a := (l_a - 1);
                -- PROCEDURE_CALL myproc(5,a) (199,5)
                myproc(5, l_a);
                -- JOIN Here (201,5) at -69, -154
                goto Here;
            end if;
            -- NEXT_STATE Running (204,10) at -8, -89
            state := Running;
            return;
        end runTransition;
        

    begin
        runTransition(0);
end orchestrator;