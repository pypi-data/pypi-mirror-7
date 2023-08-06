# -*- coding: utf-8 -*-
"""Small graphs from the ISGCI database.

http://www.graphclasses.org
Information System on Graph Classes and their Inclusions (ISGCI)
by H.N. de Ridder et al. 2001-2013
"""
import networkx as nx

smallgraphstxt = \
r"""A \cup K_1:Fr?__
\co{A \cup K_1}:FK~^W
gem \cup K_1:Eq{?
\co{gem \cup K_1}:ELBw
co-fork \cup K_1:EDaW
\co{co-fork \cup K_1}:Ey\_
net \cup K_1:FjGO?
\co{net \cup K_1}:FSvnw
P_3:Bg
\co{P_3}:BO
triangle:Bw
3K_1:B?
claw:Cs
co-claw:CJ
P_4:Ch
paw:Cx
co-paw:CE
C_4:Cr
2K_2:CK
diamond:Cz
co-diamond:CC
K_4:C~
4K_1:C?
K_5:D~{
5K_1:D??
K_{1,4}:Ds_
\co{K_{1,4}}:DJ[
K_{1,5}:Esa?
\co{K_{1,5}}:EJ\w
P_3 \cup 2K_1:Do?
\co{P_3 \cup 2K_1}:DN{
claw \cup K_1:Ds?
\co{claw \cup K_1}:DJ{
P_3 \cup P_4:Fh?GG
\co{P_3 \cup P_4}:FU~vo
3P_3:HgCG?C@
\co{3P_3}:HVzv~z}
P:DrG
\co{P}:DKs
bull:D{O
butterfly:D{c
co-butterfly:DBW
butterfly \cup K_1:E{c?
\co{butterfly \cup K_1}:EBZw
cricket:DiS
co-cricket:DTg
K_5 - e:D~k
\co{K_5 - e}:D?O
C_5:Dhc
P_2 \cup P_3:D`C
\co{P_2 \cup P_3}:D]w
W_4:Dl{
\co{W_4}:DQ?
W_4 \cup K_1:El{?
\co{W_4 \cup K_1}:EQBw
fork:DiC
co-fork:DTw
dart:DvC
co-dart:DGw
P_5:DhC
house:DUw
gem:Dh{
co-gem:DU?
K_{2,3}:D]o
K_2 \cup K_3:D`K
3K_2:E`?G
\co{3K_2}:E]~o
cross:EiD?
co-cross:ETyw
X_{37}:EhMG
\co{X_{37}}:EUpo
fish:ErCW
co-fish:EKz_
4-fan:EhFw
co-4-fan:EUw?
A:EhSG
\co{A}:EUjo
H:EgSG
\co{H}:EVjo
R:ElCO
\co{R}:EQzg
C_4 \cup P_2:El?G
\co{C_4 \cup P_2}:EQ~o
K_{3,3}:EFz_
2K_3:EwCW
K_{3,3} \cup K_1:FFz_?
\co{K_{3,3} \cup K_1}:FwC^w
3K_3:HwCW?CB
K_{3,3,3}:HFzf~z{
P_2 \cup P_4:Eh?G
\co{P_2 \cup P_4}:EU~o
E:EhC_
\co{E}:EUzW
star_{1,2,4}:Gp_GGC
co-star_{1,2,4}:GM^vvw
star_{1,2,5}:Hp_GGC@
co-star_{1,2,5}:HM^vvz}
domino:ErGW
co-domino:EKv_
domino \cup K_1:FrGW?
\co{domino \cup K_1}:FKvfw
twin-C_5:EhdG
co-twin-C_5:EUYo
X_{58}:EhFo
\co{X_{58}}:EUwG
C_6:EhEG
\co{C_6}:EUxo
C_6 \cup K_1:FhEG?
\co{C_6 \cup K_1}:FUxvw
K_{3,3}-e:EFz?
2K_3 + e:EwCw
K_{3,3}-e \cup K_1:FFz??
\co{K_{3,3}-e \cup K_1}:FwC~w
K_{3,3}+e:Efz_
K_3 \cup P_3:EWCW
2P_3:EgCG
\co{2P_3}:EVzo
X_{197}:EgC?
\co{X_{197}}:EVzw
X_{198}:EhK?
\co{X_{198}}:EUrw
X_{199}:FhCNo
\co{X_{199}}:FUzoG
6-fan:FhCNw
co-6-fan:FUzo?
X_{200}:FhENo
\co{X_{200}}:FUxoG
X_{201}:H~|_{A?
\co{X_{201}}:H?A^B|~
X_{202}:H{S{aSf
X_{203}:LhEH?C@CG?_@A@
\co{X_{203}}:LUxu~z}zv~^}|}
X_{98}:Elhg
\co{X_{98}}:EQUO
S_3:Ey[g
net:EDbO
S_3 \cup K_1:Fy[g?
\co{S_3 \cup K_1}:FDbVw
X_{18}:ElCG
\co{X_{18}}:EQzo
X_5:E|EG
\co{X_5}:EAxo
P_6:EhCG
\co{P_6}:EUzo
W_5:Ehfw
\co{W_5}:EUW?
5-pan:EhcG
\co{5-pan}:EUZo
6-pan:FhEGG
\co{6-pan}:FUxvo
C_4 \cup 2K_1:El??
\co{C_4 \cup 2K_1}:EQ~w
K_3 \cup 2K_1:Dw?
\co{K_3 \cup 2K_1}:DF{
antenna:EjCg
co-antenna:ESzO
X_{45}:EhQg
\co{X_{45}}:EUlO
twin-house:Elr?
co-twin-house:EQKw
C_7:FhCKG
\co{C_7}:FUzro
X_{12}:FrYxw
\co{X_{12}}:FKdE?
X_{13}:FlwWG
\co{X_{13}}:FQFfo
X_{36}:FhhWW
\co{X_{36}}:FUUf_
X_{42}:FxE\g
\co{X_{42}}:FExaO
X_{11}:FrYXw
\co{X_{11}}:FKde?
X_{35}:FhFj?
\co{X_{35}}:FUwSw
X_{41}:FhO_W
\co{X_{41}}:FUn^_
X_{70}:FHFv_
\co{X_{70}}:FuwGW
longhorn:FhCH_
co-longhorn:FUzuW
T_2:FhC_G
\co{T_2}:FUz^o
X_{14}:FlwWW
\co{X_{14}}:FQFf_
X_{20}:FhCiG
\co{X_{20}}:FUzTo
X_{34}:Fy\HG
\co{X_{34}}:FDauo
X_{40}:FhhoW
\co{X_{40}}:FUUN_
X_{38}:FhCKg
\co{X_{38}}:FUzrO
X_{32}:FhFh?
\co{X_{32}}:FUwUw
X_9:FhEhO
\co{X_9}:FUxUg
P_7:FhCGG
\co{P_7}:FUzvo
X_3:FrGX?
\co{X_3}:FKvew
X_2:FhDOG
\co{X_2}:FUyno
X_1:Fy\`G
\co{X_1}:FDa]o
X_8:FrGWW
\co{X_8}:FKvf_
X_7:Fl_GW
\co{X_7}:FQ^v_
X_6:Fl_GO
\co{X_6}:FQ^vg
star_{1,2,3}:FhCG_
\co{star_{1,2,3}}:FUzvW
X_{33}:FhEj?
\co{X_{33}}:FUxSw
rising sun:F~p`_
co-rising sun:F?M]W
X_{10}:FrGXW
\co{X_{10}}:FKve_
X_{27}:FlGHG
\co{X_{27}}:FQvuo
X_{39}:FhhOW
\co{X_{39}}:FUUn_
X_{17}:FrCZW
\co{X_{17}}:FKzc_
X_{46}:FhUjW
\co{X_{46}}:FUhS_
X_{15}:Flw[W
\co{X_{15}}:FQFb_
W_6:FqG^w
\co{W_6}:FLv_?
W_7:GhCKN{
\co{W_7}:GUzro?
BW_3:FqG[o
\co{BW_3}:FLvbG
X_{31}:FhFx?
\co{X_{31}}:FUwEw
X_{30}:FhOgW
\co{X_{30}}:FUnV_
parachute:F|dwG
parapluie:FAYFo
X_{82}:FvKxO
\co{X_{82}}:FGrEg
P_8:GhCGGC
\co{P_8}:GUzvvw
X_{50}:GhEhh[
\co{X_{50}}:GUxUU_
K_{4,4}:G?~vf_
2K_4:G~?GW[
X_{52}:GhElh[
\co{X_{52}}:GUxQU_
X_{74}:G?pk`c
\co{X_{74}}:G~MR]W
X_{80}:GhELQk
\co{X_{80}}:GUxqlO
X_{51}:GhElH[
\co{X_{51}}:GUxQu_
X_{22}:GhSIhC
\co{X_{22}}:GUjtUw
X_{53}:GhElj[
\co{X_{53}}:GUxQS_
2C_4:Gl?GGS
\co{2C_4}:GQ~vvg
X_{47}:GhEhhW
\co{X_{47}}:GUxUUc
X_{49}:GhElhW
\co{X_{49}}:GUxQUc
X_{26}:GkQAhS
\co{X_{26}}:GRl|Ug
X_{19}:GhCI@C
\co{X_{19}}:GUzt}w
X_{77}:GxEG_G
\co{X_{77}}:GExv^s
X_{48}:GhElHW
\co{X_{48}}:GUxQuc
X_{25}:GDhXGo
\co{X_{25}}:GyUevK
X_{28}:GlUad?
\co{X_{28}}:GQh\Y{
S_4:G~fB@_
X_{178}:GnfB@_
\co{X_{178}}:GOW{}[
X_{179}:H{OebQc
\co{X_{179}}:HBnX[lZ
X_{180}:G|?GWS
\co{X_{180}}:GA~vfg
X_{181}:G|GGWS
\co{X_{181}}:GAvvfg
X_{182}:Gh{GGK
\co{X_{182}}:GUBvvo
X_{183}:IgCNwC@?W
\co{X_{183}}:IVzoFz}~_
sunlet_4:Gl`@?_
\co{sunlet_4}:GQ]}~[
X_{185}:GhRHhC
\co{X_{185}}:GUkuUw
X_{186}:Ghqihc
X_{187}:Glqihc
\co{X_{187}}:GQLTUW
X_{188}:Glqihs
\co{X_{188}}:GQLTUG
X_{189}:GhdWJS
\co{X_{189}}:GUYfsg
X_{190}:GVWs]G
\co{X_{190}}:GgfJ`s
X_{191}:GhfPYS
\co{X_{191}}:GUWmdg
X_{192}:GhfPYs
\co{X_{192}}:GUWmdG
X_{193}:Gheml_
\co{X_{193}}:GUXPQ[
X_{194}:IAzpsX_WG
\co{X_{194}}:I|CMJe^fo
X_{164}:Gl`H?c
\co{X_{164}}:GQ]u~W
X_{165}:Gl`H?_
\co{X_{165}}:GQ]u~[
X_{166}:EhD_
\co{X_{166}}:EUyW
X_{167}:EhTO
\co{X_{167}}:EUig
X_{168}:EhPo
\co{X_{168}}:EUmG
X_{169}:EhGg
\co{X_{169}}:EUvO
X_{170}:EhGw
\co{X_{170}}:EUv?
X_{171}:EhCw
\co{X_{171}}:EUz?
X_{172}:EhCO
\co{X_{172}}:EUzg
X_{173}:FhEKG
\co{X_{173}}:FUxro
X_{174}:IheAHCPBG
\co{X_{174}}:IUX|uzm{o
X_{175}:FhFrw
\co{X_{175}}:FUwK?
X_{176}:FhCJo
\co{X_{176}}:FUzsG
X_{177}:FhCO?
\co{X_{177}}:FUznw
claw \cup 3K_1:Fs???
\co{claw \cup 3K_1}:FJ~~w
X_{29}:G?bFF_
\co{X_{29}}:G~[ww[
C_8:GhCGKC
\co{C_8}:GUzvrw
X_{195}:IzKWWMBoW
\co{X_{195}}:ICrffp{N_
X_{196}:L~[ww[F?{BwFwF
\co{X_{196}}:L?bFFbw~B{FwFw
X_{71}:GiGWGO
\co{X_{71}}:GTvfvk
X_{79}:GhELQg
\co{X_{79}}:GUxqlS
X_{83}:GjbiJC
\co{X_{83}}:GS[Tsw
X_{84}:ElD?
\co{X_{84}}:EQyw
X_{85}:FhD?_
\co{X_{85}}:FUy~W
X_{86}:Fhfco
\co{X_{86}}:FUWZG
X_{87}:Fhdiw
\co{X_{87}}:FUYT?
X_{88}:Fy[kg
\co{X_{88}}:FDbRO
X_{89}:FhfJo
\co{X_{89}}:FUWsG
X_{90}:Fhfmo
\co{X_{90}}:FUWPG
X_{91}:HgCg?Cd
\co{X_{91}}:HVzV~zY
X_{92}:FErF?
\co{X_{92}}:FxKww
X_{93}:FErf?
\co{X_{93}}:FxKWw
X_{94}:HgSG?S@
\co{X_{94}}:HVjv~j}
X_{95}:EXCW
\co{X_{95}}:Eez_
X_{96}:EgTg
\co{X_{96}}:EViO
claw \cup triangle:Fs?GW
\co{claw \cup triangle}:FJ~v_
X_{97}:F~Gwg
\co{X_{97}}:F?vFO
X_{99}:FFzc?
\co{X_{99}}:FwCZw
X_{100}:FgCNw
\co{X_{100}}:FVzo?
X_{101}:FwC\g
\co{X_{101}}:FFzaO
X_{102}:FgC^g
\co{X_{102}}:FVz_O
X_{184}:F^rCW
\co{X_{184}}:F_Kz_
X_{103}:FxmLO
\co{X_{103}}:FEPqg
X_{104}:FxELO
co-X_{104}:FExqg
X_{105}:FhFNW
\co{X_{105}}:FUwo_
X_{108}:GUzrv{
\co{X_{108}}:GhCKG?
X_{109}:GhCMLw
\co{X_{109}}:GUzpqC
X_{110}:G{iuLw
\co{X_{110}}:GBTHqC
X_{111}:GhKMKg
\co{X_{111}}:GUrprS
X_{112}:GjCMNW
\co{X_{112}}:GSzpoc
X_{113}:GxCJLw
\co{X_{113}}:GEzsqC
X_{114}:GVvJuC
\co{X_{114}}:GgGsHw
X_{106}:FjFLw
\co{X_{106}}:FSwq?
X_{107}:FhmLO
\co{X_{107}}:FUPqg
X_{115}:GRvNUC
\co{X_{115}}:GkGohw
X_{116}:GVrRMw
\co{X_{116}}:GgKkpC
X_{117}:GR~eNW
\co{X_{117}}:Gk?Xoc
X_{118}:Gb[MNW
\co{X_{118}}:G[bpoc
X_{119}:G}CJi{
\co{X_{119}}:G@zsT?
X_{120}:GhKM[{
\co{X_{120}}:GUrpb?
X_{121}:GxKJKg
\co{X_{121}}:GErsrS
X_{122}:G{guHo
\co{X_{122}}:GBVHuK
X_{123}:G[X}J_
\co{X_{123}}:Gbe@s[
X_{124}:GkirLw
\co{X_{124}}:GRTKqC
X_{125}:GvvLuC
\co{X_{125}}:GGGqHw
X_{126}:GSW]J_
\co{X_{126}}:Gjf`s[
X_{127}:F`GV_
\co{X_{127}}:F]vgW
X_{128}:FhV]o
\co{X_{128}}:FUg`G
X_{129}:FhCeo
\co{X_{129}}:FUzXG
X_{130}:FhDAG
\co{X_{130}}:FUy|o
X_{131}:GJEw[_
\co{X_{131}}:GsxFb[
X_{132}:FhDEg
\co{X_{132}}:FUyxO
X_{133}:Fh}`_
\co{X_{133}}:FU@]W
X_{134}:FhDWG
\co{X_{134}}:FUyfo
X_{135}:GHPjn?
\co{X_{135}}:GumSO{
X_{136}:GXPjn?
\co{X_{136}}:GemSO{
X_{137}:GxPjn?
\co{X_{137}}:GEmSO{
X_{138}:HQr?OJK
\co{X_{138}}:HlK~nsr
X_{139}:HQr?OJk
\co{X_{139}}:HlK~nsR
X_{140}:HQr?OJm
\co{X_{140}}:HlK~nsP
X_{141}:HQR?OJm
\co{X_{141}}:Hlk~nsP
X_{142}:Gl_fa_
\co{X_{142}}:GQ^W\[
X_{143}:Gl_fq_
\co{X_{143}}:GQ^WL[
X_{144}:Gl`fa_
\co{X_{144}}:GQ]W\[
X_{145}:Glpfa_
\co{X_{145}}:GQMW\[
X_{146}:Gl`fi_
\co{X_{146}}:GQ]WT[
X_{147}:Gh`fy_
\co{X_{147}}:GU]WD[
X_{148}:Gl`fq_
\co{X_{148}}:GQ]WL[
X_{149}:Glpfq_
\co{X_{149}}:GQMWL[
X_{150}:Glpfy_
\co{X_{150}}:GQMWD[
X_{151}:Gl`fy_
\co{X_{151}}:GQ]WD[
X_{152}:GO?O~C
\co{X_{152}}:Gn~n?w
X_{153}:HO?O~Nr
\co{X_{153}}:Hn~n?oK
X_{154}:HO?O~Mr
\co{X_{154}}:Hn~n?pK
X_{155}:IO?P{~f{w
\co{X_{155}}:In~mB?WB?
X_{156}:IO?P{~fkw
\co{X_{156}}:In~mB?WR?
X_{157}:IO?Pk~fkw
\co{X_{157}}:In~mR?WR?
X_{158}:IOAPk~fkw
\co{X_{158}}:In|mR?WR?
X_{159}:FJTNo
\co{X_{159}}:FsioG
X_{160}:GjTJwC
X_{161}:GjTjwC
\co{X_{161}}:GSiSFw
X_{162}:FJTno
\co{X_{162}}:FsiOG
X_{163}:Ehp_
\co{X_{163}}:EUMW
K_{3,4}-e:FEzf?
\co{K_{3,4}-e}:FxCWw
K_{3,4}:FFzf?
K_3 \cup K_4:FwCWw
P_9:HhCGGC@
\co{P_9}:HUzvvz}
X_{24}:HLCgLS@
\co{X_{24}}:HqzVqj}
X_{73}:HhEI?_C
\co{X_{73}}:HUxt~^z
X_{21}:HhSIgC_
\co{X_{21}}:HUjtVz^
X_{43}:HhD@GcA
\co{X_{43}}:HUy}vZ|
X_{55}:HhEljZc
\co{X_{55}}:HUxQScZ
X_{54}:HhEljYs
\co{X_{54}}:HUxQSdJ
BW_4:HhCGKEi
\co{BW_4}:HUzvrxT
X_{56}:HhEljZ{
\co{X_{56}}:HUxQScB
X_{23}:HhSIkCa
\co{X_{23}}:HUjtRz\
X_{72}:IheMB?oE?
\co{X_{72}}:IUXp{~Nxw
X_{75}:IhEI@?CA?
\co{X_{75}}:IUxt}~z|w
X_4:IhEFHCxAG
\co{X_4}:IUxwuzE|o
X_{76}:IhEI@CCAG
\co{X_{76}}:IUxt}zz|o
X_{81}:IkCOK?@A?
\co{X_{81}}:IRznr~}|w
T_3:IhCGG_@?G
\co{T_3}:IUzvv^}~o
X_{44}:IhCH?cA?W
\co{X_{44}}:IUzu~Z|~_
X_{59}:JhC?GC@?HA?
\co{X_{59}}:JUz~vz}~u|_
X_{57}:JhEljXz{@y_
\co{X_{57}}:JUxQSeCB}D?
K_2 \cup claw:Es?G
\co{K_2 \cup claw}:EJ~o
2P_4:Gh?GGC
\co{2P_4}:GU~vvw
eiffeltower:FhCoG
co-eiffeltower:FUzNo"""
smallgraphs = {}
for line in smallgraphstxt.split('\n'):
    name,g6=line.split(':')
    print name,g6
    smallgraphs[name]=nx.parse_graph6(g6)
