import unittest
import peeringdb as pb

class testpeeringdb(unittest.TestCase):
    def test_getix(self):
        asn = 49909
        expected1 = ["Balcan-IX","RoNIX","InterLAN"]
        expected2 = 5000
        result1, result2 = pb.getIX(asn)
        self.assertEqual(result1, expected1)
        self.assertEqual(result2, expected2)


    def test_findpeerings(self):
        asn = 49909
        ix_name = "Balcan-IX"
        expected = ['Ad Net Market Media SA', 'BALCAN-IX Route Servers', 'BALCAN-IX Route Servers', 'Cloudflare', 'DOTRO Telecom', 'Distinct New Media', 'Expansion Computers', 'Facebook Inc', 'Facebook Inc', 'Hurricane Electric', 'I.S. Centrul de Telecomunicatii Speciale', 'IPTP Networks', 'Infinity Telecom SRL', 'M247', 'M247', 'Microsoft', 'Microsoft', 'Moldtelecom', 'NAV Communications', 'Neotel', 'Neterra Ltd.', 'Pixel View SRL', 'Prime Telecom', 'RoEduNet', 'Serbia BroadBand', 'Serbian Open eXchange', 'TENNET TELECOM', 'TV SAT 2002', 'TeenTelecom', 'Telehouse', 'Telehouse', 'Telekom Romania Communications S.A.', 'Türk Telekom International', 'VOXILITY', 'Valve Corporation', 'Valve Corporation', 'Verizon Digital Media Services (EdgeCast Networks)', 'Yahoo!']
        result = pb.findPeerings(ix_name,asn)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
