import unittest
import peeringdb as pb

class testpeeringdb(unittest.TestCase):
    def test_lookupNet(self):
        expected = "Twitch"
        result = pb.lookupNet(1956)
        self.assertEqual(result, expected)

    def test_getix(self):
        asn = 49909
        expected1 = ["Balcan-IX","InterLAN","RoNIX"]
        expected2 = 5000
        result1, result2 = pb.getIX(asn)
        self.assertEqual(result1, expected1)
        self.assertEqual(result2, expected2)


    def test_findpeerings(self):
        asn = 49909
        ix_name = "Balcan-IX"
        expected = [  "AS_10310_Yahoo!","AS_13004_Serbian Open eXchange","AS_13335_Cloudflare","AS_15133_Verizon Digital Media Services (EdgeCast Networks)","AS_24745_BALCAN-IX Route Servers","AS_24745_BALCAN-IX Route Servers","AS_2614_RoEduNet",
        "AS_31042_Serbia BroadBand","AS_3223_VOXILITY","AS_32590_Valve Corporation","AS_32590_Valve Corporation","AS_32934_Facebook Inc","AS_32934_Facebook Inc","AS_34224_Neterra Ltd.","AS_34304_TeenTelecom",
        "AS_34772_Neotel","AS_35711_Expansion Computers","AS_39279_I.S. Centrul de Telecomunicatii Speciale","AS_39543_TENNET TELECOM","AS_39737_Prime Telecom","AS_41095_IPTP Networks","AS_41496_TV SAT 2002",
        "AS_43376_DOTRO Telecom","AS_48067_Distinct New Media","AS_50244_Pixel View SRL","AS_5541_Ad Net Market Media SA","AS_56654_Infinity Telecom SRL","AS_57344_Telehouse","AS_57344_Telehouse","AS_6663_T\u00fcrk Telekom International",
        "AS_6718_NAV Communications","AS_6939_Hurricane Electric","AS_8075_Microsoft","AS_8075_Microsoft","AS_8926_Moldtelecom","AS_9009_M247","AS_9009_M247","AS_9050_Telekom Romania Communications S.A."]
        result = pb.findPeerings(ix_name,asn)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
