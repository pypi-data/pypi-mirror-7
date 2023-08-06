-- This file was generated automatically: DO NOT MODIFY IT !

with TASTE_Dataview;
use TASTE_Dataview;

package og is
    --  Provided interface "Go"
    procedure Go(ze_param: access asn1SccMy_OctStr);
    --  Required interface "rezult"
    procedure rezult(ze_rezult: access asn1SccMy_OctStr);
    pragma import(C, rezult, "og_RI_rezult");
end og;