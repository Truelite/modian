# live-wrapper - Wrapper for vmdebootstrap for creating live images
# coding: utf8
# (C) Iain R. Learmonth 2015 <irl@debian.org>
# See COPYING for terms of usage, modification and redistribution.
#
# lwr/bootloader.py - Bootloader helpers

import os


class BootloaderConfig(object):

    def __init__(self, cdroot, bootappend, timeout=None):
        self.cdroot = cdroot
        self.bootappend = bootappend
        self.entries = []
        self.timeout = timeout

    def add_live(self):
        # FIXME: need declarative paths
        self.versions = detect_kernels(self.cdroot)
        self.versions.sort(reverse=True)

        cmdline = "boot=live components"
        if self.bootappend:
            cmdline += " " + self.bootappend

        for version in self.versions:
            self.entries.append({
                                 'description': 'Debian GNU/Linux Live (kernel %s)' % (version,),
                                 'type': 'linux',
                                 'kernel': '/live/vmlinuz-%s' % (version,),
                                 'cmdline': cmdline,
                                 'initrd': '/live/initrd.img-%s' % (version,),
                                })

    def add_installer(self, kernel, ramdisk):  # pylint: disable=no-self-use
        self.entries.append({
                             'description': 'Graphical Debian Installer',
                             'type': 'linux',
                             'kernel': '/d-i/gtk/%s' % (os.path.basename(kernel),),
                             'initrd': '/d-i/gtk/%s' % (os.path.basename(ramdisk),),
                             'cmdline': 'append video=vesa:ywrap,mtrr vga=788'
                            })
        self.entries.append({
                             'description': 'Debian Installer',
                             'type': 'linux',
                             'kernel': '/d-i/%s' % (os.path.basename(kernel),),
                             'initrd': '/d-i/%s' % (os.path.basename(ramdisk),),
                            })
        self.entries.append({
                             'description': 'Debian Installer with Speech Synthesis',
                             'type': 'linux',
                             'kernel': '/d-i/gtk/%s' % (os.path.basename(kernel),),
                             'initrd': '/d-i/gtk/%s' % (os.path.basename(ramdisk),),
                             'cmdline': 'speakup.synth=soft',
                            })

    def add_live_localisation(self):
        # FIXME: need declarative paths
        self.versions = detect_kernels(self.cdroot)
        self.versions.sort(reverse=True)
        lines = [
            u"#",
            u"# This is the complete list of languages (locales) to choose from.",
            u"# langcode;language (en);language (orig);supported_environments;countrycode;fallbacklocale;langlist;console-setup",
            u"sq;Albanian;Shqip;2;AL;sq_AL.UTF-8;;console-setup",
            u"am;Amharic;????????????;4;ET;am_ET;;",
            u"ar;Arabic;????????;3;EG;ar_EG.UTF-8;;console-setup",
            u"ast;Asturian;Asturianu;2;ES;ast_ES.UTF-8;;console-setup",
            u"eu;Basque;Euskara;1;ES;eu_ES.UTF-8;;console-setup",
            u"be;Belarusian;????????????????????;2;BY;be_BY.UTF-8;;console-setup",
            u"bn;Bangla;???????????????;4;BD;bn_BD;;",
            u"bs;Bosnian;Bosanski;2;BA;bs_BA.UTF-8;;console-setup",
            u"#X br;Breton;Brezhoneg;2;FR;br_FR.UTF-8;;console-setup",
            u"bg;Bulgarian;??????????????????;2;BG;bg_BG.UTF-8;;console-setup",
            u"bo;Tibetan;?????????????????????;4;IN;bo_IN;;",
            u"# For C locale, set language to 'en' to make sure questions are \"translated\"",
            u"# to English instead of showing codes.",
            u"C;C;No localization;0;;C;en;",
            u"ca;Catalan;Catal??;1;ES;ca_ES.UTF-8;;console-setup",
            u"# Special case for Chinese as the two flavours share the same ISO 639 code",
            u"# Both will trigger countrychooser. Each will be the backup for the other",
            u"# one",
            u"zh_CN;Chinese (Simplified);??????(??????);3;CN;zh_CN.UTF-8;zh_CN:zh;",
            u"zh_TW;Chinese (Traditional);??????(??????);3;TW;zh_TW.UTF-8;zh_TW:zh;",
            u"#X the;Chitwania Tharu;????????????;4;NP;the_NP;;console-setup",
            u"hr;Croatian;Hrvatski;2;HR;hr_HR.UTF-8;;console-setup",
            u"cs;Czech;??e??tina;2;CZ;cs_CZ.UTF-8;;console-setup",
            u"da;Danish;Dansk;1;DK;da_DK.UTF-8;;console-setup",
            u"nl;Dutch;Nederlands;1;NL;nl_NL.UTF-8;;console-setup",
            u"dz;Dzongkha;?????????????????????;4;BT;dz_BT;;",
            u"en;English;English;0;US;en_US.UTF-8;;console-setup",
            u"# The Esperanto locale is eo.UTF-8",
            u"# so no country on purpose. The default country is Antarctica because...",
            u"# ...why not..:-)",
            u"eo;Esperanto;Esperanto;2;AQ;eo.UTF-8;;console-setup",
            u"et;Estonian;Eesti;2;EE;et_EE.UTF-8;;console-setup",
            u"fi;Finnish;Suomi;1;FI;fi_FI.UTF-8;;console-setup",
            u"fr;French;Fran??ais;1;FR;fr_FR.UTF-8;;console-setup",
            u"gl;Galician;Galego;1;ES;gl_ES.UTF-8;;console-setup",
            u"ka;Georgian;?????????????????????;4;GE;ka_GE.UTF-8;;console-setup",
            u"de;German;Deutsch;1;DE;de_DE.UTF-8;;console-setup",
            u"el;Greek;????????????????;2;GR;el_GR.UTF-8;;console-setup",
            u"gu;Gujarati;?????????????????????;4;IN;gu_IN;;",
            u"he;Hebrew;??????????;3;IL;he_IL.UTF-8;;console-setup",
            u"hi;Hindi;?????????????????? ;4;IN;hi_IN;;",
            u"hu;Hungarian;Magyar;2;HU;hu_HU.UTF-8;;console-setup",
            u"is;Icelandic;??slenska;1;IS;is_IS.UTF-8;;console-setup",
            u"id;Indonesian;Bahasa Indonesia;1;ID;id_ID.UTF-8;;console-setup",
            u"ga;Irish;Gaeilge;1;IE;ga_IE.UTF-8;;console-setup",
            u"it;Italian;Italiano;1;IT;it_IT.UTF-8;;console-setup",
            u"#X jam;Jamaican Creole English;Jamaican Creole English;1;JM;jam_JM;;console-setup",
            u"ja;Japanese;?????????;3;JP;ja_JP.UTF-8;;",
            u"#X ks;Kashmiri;???????????????;4;IN;ks_IN;;",
            u"kk;Kazakh;??????????;2;KZ;kk_KZ.UTF-8;;console-setup",
            u"km;Khmer;??????????????????;4;KH;km_KH;;",
            u"kn;Kannada;???????????????;4;IN;kn_IN;;",
            u"ko;Korean;?????????;3;KR;ko_KR.UTF-8;;",
            u"ku;Kurdish;Kurd??;2;TR;ku_TR.UTF-8;;console-setup",
            u"#X ky;Kirghiz;????????????????;2;KG;ky_KG;;console-setup",
            u"lo;Lao;????????????;4;LA;lo_LA;;console-setup",
            u"lv;Latvian;Latviski;2;LV;lv_LV.UTF-8;;console-setup",
            u"lt;Lithuanian;Lietuvi??kai;2;LT;lt_LT.UTF-8;;console-setup",
            u"#X mg;Malagasy;Malagasy;1;MG;mg_MG.UTF-8;mg_MG:fr_FR:fr:en;console-setup",
            u"#X ms;Malay;Bahasa Malaysia;1;MY;ms_MY.UTF-8;;console-setup",
            u"ml;Malayalam;??????????????????;4;IN;ml_IN;;",
            u"mr;Marathi;???????????????;4;IN;mr_IN;;",
            u"mk;Macedonian;????????????????????;2;MK;mk_MK.UTF-8;;console-setup",
            u"my;Burmese; ???????????????????????????;4;MM;my_MM;;",
            u"ne;Nepali;?????????????????? ;4;NP;ne_NP;;",
            u"# The Sami translation is really incomplete. We however keep Sami on request",
            u"# of Skolelinux as a kind of reward to them..:-). They need to be able to",
            u"# choose Sami as an option so that the Sami locale is set as default",
            u"se_NO;Northern Sami;S??megillii;1;NO;se_NO;se_NO:nb_NO:nb:no_NO:no:nn_NO:nn:da:sv:en;console-setup",
            u"nb_NO;Norwegian Bokmaal;Norsk bokm??l;1;NO;nb_NO.UTF-8;nb_NO:nb:no_NO:no:nn_NO:nn:da:sv:en;console-setup",
            u"nn_NO;Norwegian Nynorsk;Norsk nynorsk;1;NO;nn_NO.UTF-8;nn_NO:nn:no_NO:no:nb_NO:nb:da:sv:en;console-setup",
            u"#X os;Ossetian;???????? ??????????;3;RU;os_RU;;console-setup",
            u"fa;Persian;??????????;3;IR;fa_IR;;console-setup",
            u"pl;Polish;Polski;2;PL;pl_PL.UTF-8;;console-setup",
            u"pt;Portuguese;Portugu??s;1;PT;pt_PT.UTF-8;pt:pt_BR:en;console-setup",
            u"pt_BR;Portuguese (Brazil);Portugu??s do Brasil;1;BR;pt_BR.UTF-8;pt_BR:pt:en;console-setup",
            u"pa;Punjabi (Gurmukhi);??????????????????;4;IN;pa_IN;;",
            u"ro;Romanian;Rom??n??;2;RO;ro_RO.UTF-8;;console-setup",
            u"ru;Russian;??????????????;2;RU;ru_RU.UTF-8;;console-setup",
            u"#X sa;Sanskrit;?????????????????????;4;IN;sa_IN;;",
            u"#X sd;Sindhi;????????;3;PK;sd_PK.UTF-8;;console-setup",
            u"si;Sinhala;???????????????;4;LK;si_LK;;",
            u"sr;Serbian (Cyrillic);????????????;2;RS;sr_RS;;console-setup",
            u"#X sr@latin;Serbian (Latin);Srpski;2;RS;sr_RS@latin;;console-setup",
            u"sk;Slovak;Sloven??ina;2;SK;sk_SK.UTF-8;;console-setup",
            u"sl;Slovenian;Sloven????ina;2;SI;sl_SI.UTF-8;;console-setup",
            u"es;Spanish;Espa??ol;1;ES;es_ES.UTF-8;;console-setup",
            u"sv;Swedish;Svenska;1;SE;sv_SE.UTF-8;;console-setup",
            u"tl;Tagalog;Tagalog;1;PH;tl_PH.UTF-8;;console-setup",
            u"ta;Tamil;???????????????;4;IN;ta_IN;;",
            u"te;Telugu;??????????????????;4;IN;te_IN;;",
            u"tg;Tajik;????????????;2;TJ;tg_TJ.UTF-8;;console-setup",
            u"th;Thai;?????????????????????;3;TH;th_TH.UTF-8;;console-setup",
            u"tr;Turkish;T??rk??e;2;TR;tr_TR.UTF-8;;console-setup",
            u"ug;Uyghur;????????????????;3;CN;ug_CN;;",
            u"uk;Ukrainian;????????????????????;2;UA;uk_UA.UTF-8;;console-setup",
            u"#X ur;Urdu;????????;3;PK;ur_PK.UTF-8;;console-setup",
            u"#X ca@valencia;Valencian-Catalan;Valenci??-Catal??;1;ES;ca_ES.UTF-8@valencia;;console-setup",
            u"vi;Vietnamese;Ti???ng Vi???t;3;VN;vi_VN;;console-setup",
            u"cy;Welsh;Cymraeg;2;GB;cy_GB.UTF-8;;console-setup",
            u"#X wo;Wolof;Wolof;2;SN;wo_SN;wo:fr:en;",
            u"#X xh;Xhosa;Xhosa;2;ZA;xh_ZA.UTF-8;;console-setup",
        ]
        lang_lines = [line for line in lines if not line.startswith('#')]

        for line in lang_lines:
            language = line.split(';')
            cmdline = "boot=live components locales=" + language[5]
            if self.bootappend:
                cmdline += " " + self.bootappend
            for version in self.versions:
                self.entries.append({
                                 'description': '%s (%s)' % (language[1], language[0],),
                                 'type': 'linux',
                                 'kernel': '/live/vmlinuz-%s' % (version,),
                                 'cmdline': cmdline,
                                 'initrd': '/live/initrd.img-%s' % (version,),
                                })

    def add_submenu(self, description, loadercfg):
        self.entries.append({
                             'description': '%s' % (description),
                             'type': 'menu',
                             'subentries': loadercfg,
                            })

    def is_empty(self, supported_types):
        for entry in self.entries:
            if entry['type'] in supported_types:
                print("Found %r in %r" % (entry, supported_types,))
                return False
        return True


def detect_kernels(cdroot):
    versions = []
    filenames = os.listdir(os.path.join(cdroot, "live"))
    for filename in filenames:
        if filename[0:8] == "vmlinuz-":
            versions.append(filename[8:])
    return versions
