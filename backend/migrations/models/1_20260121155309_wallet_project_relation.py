from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `project_account` DROP FOREIGN KEY `fk_project__project__93399a32`;
        ALTER TABLE `project_account` DROP INDEX `idx_project_acc_wallet__29c3f9`;
        ALTER TABLE `project_account` DROP COLUMN `wallet_id`;
        ALTER TABLE `project_wallet` ADD `project_id` CHAR(36) NOT NULL COMMENT '所属项目';
        ALTER TABLE `project_wallet` ADD CONSTRAINT `fk_project__project__cba39da5` FOREIGN KEY (`project_id`) REFERENCES `project_info` (`id`) ON DELETE CASCADE;
        ALTER TABLE `project_wallet` ADD INDEX `idx_project_wal_project_7a4c7e` (`project_id`, `chain`, `create_time`);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `project_wallet` DROP INDEX `idx_project_wal_project_7a4c7e`;
        ALTER TABLE `project_wallet` DROP FOREIGN KEY `fk_project__project__cba39da5`;
        ALTER TABLE `project_wallet` DROP COLUMN `project_id`;
        ALTER TABLE `project_account` ADD `wallet_id` CHAR(36) COMMENT '关联钱包信息';
        ALTER TABLE `project_account` ADD CONSTRAINT `fk_project__project__93399a32` FOREIGN KEY (`wallet_id`) REFERENCES `project_wallet` (`id`) ON DELETE CASCADE;
        ALTER TABLE `project_account` ADD INDEX `idx_project_acc_wallet__29c3f9` (`wallet_id`);"""


MODELS_STATE = (
    "eJztXWtv4zYW/SuBP00Bdyrr7WCxQDKTabNNJsUksy3aKQxZomJtbMmV5ZkERf77ktSL1M"
    "ukJVtKyi+GLfHK0rkUyXPuJfn3aBU4YLl5e7GyvOWl7waj05O/R761AvBL+eT4ZGSt1/kp"
    "dCCy5ktcGqBiMy8tN99EoWVH8IxrLTcAHnLAxg69deQFPir/ZTuVLPBla8znky9b1QXwU5"
    "d0F1k7gQ3NPf9+V8Gt7/21BbMouAfRAoSw+B9/wsOe74BHsEE//xhtIiva4nvdgPArCGee"
    "g37YIbAiaOrBh4U2ZLnyKdIwKYdPbNdOXhL98/ph5npg6VBAxnb4+Cx6WuNjnz9fvv+AS6"
    "Lnnc/sYLld+Xnp9VO0CPys+HbrOW+RDTp3D3wQwv91CHT97XKZuCI9FIMDD0ThFmSoOPkB"
    "B7jWdol8NPqXu/Vt5JoT/E/oQ/33qOy1+AZI/6A/RpgFPvK450cI9r+f46fKnxkfHaFLvP"
    "vp7NMbRf8OP2Wwie5DfBIjMnrGhlZkxabYhTmQpGNKiL6Hp9CZalQLpgV4ncT2bfplH5jT"
    "Aw04J2CVXgVNnszhJywH67bm6rDOa67KBvUIPplz4y+fkj9sgP7u8vri9u7s+hd05dVm89"
    "cSA3d2d4HOyPjoU+Hom9hTAXyb4xc9u8jJr5d3P52gnye/33y8KPozK3f3+wjdk7WNgpkf"
    "fJtZDoFNejTFD5bM/U2+Xpz+Lpgex995U7fL4bruqsjVc+kf7PDk5nN/4z6k7Ol3Cyus9n"
    "JmUPAvhOswDWWdP8kuSlNcg9GTK+txtgT+fbSAPzWpwZP/PfuEG05NKnjnY3JGxqeeKTzX"
    "1mbzLQgrup878BhVQ0radINqm/dEm9vw3TBMadK637m7+O2Oeg1S5N5cn/32HfUqXN18/D"
    "EtTiD97urmvICwtX30lp4VPs24626Faf94m66poe7ImpJ1ehi1uQDYbJ/a3XSNoaI//LfA"
    "XnrAj2ZV49z6+k8Z7YV90jp31NBYMuyKZcWAQFvAjW9rAJXetsFmAxnOA/C5KnrBrmeAi7"
    "czvDocAheOYxb8SJcMe4a6dD/Dwzqn2jTIl3504W9XGOdLeIeWb4MS3rlxAWj4NIdqsCdV"
    "TYYhz3UkRUiTN5NT+GWuK4jDKeZYhj81V5Ljn98xtiT36G6+V2RDN+FZfLPoh9Hgndvrs6"
    "ury493RXxJvYJVd6CMWsgPXbbKKgAQU0OV9CaJqGsJAgk57kOlAhGDVIb1QxAC797/GTyV"
    "Km8BykRVu8UXSmW1lwVpfjS/t9D6lilfdFWCzw6fGETxcODs9t3Z+4sRxnhu2Q/frNCZUW"
    "CjM4EcFI5kZcunVvKqeMTyrXuMC3oOdNcU6me2HWzxzZfETrrAuEnwXIfB49PMIooyaJ66"
    "ITl4hIdGdbpuwjGfI+vVnJGhOIv+ud1Ua55CrhRypZArhVwp5Mp95UrUsuLvJWfXs17S5l"
    "CCA/N7bGiymZJeTZX2oryKzkB5laKTcsqLTr1e1fLL1nUlE3fhUnpcm2voiGSZ+Ox0mByN"
    "GDawDgUIkw75w/6ivDYx4FDXlDSVruo9MgmeYS/ti7IjbnxwF8APRsbxebM33xiMC3YyD6"
    "IKMvCODrjEOzT6D59GtVwiLdDIJRLCZBNlGciEpruIHcznjVSusSBfAoXgD4I/CP4g+IPg"
    "D53wh80iCKMZL4OgrfpOfCC7FmNuQv8aU1fah0jIDDxCrqURcpFF8MJ6aFLGwR4ISBEraw"
    "EpSzhSrg9HyqVwpIjcdB+54SAJpRDPfRhs1xX+OE/MP/z8CSwt/OS1xCAep/6IrtRfVW9H"
    "A54PHzSI8akd5mfw7Rzk32clWYb4MorTGMBWdw3xawuyDPET4kFnOBcH/A1J0oILCC4guI"
    "DgAoIL7MsF+h2uthj/E/2OGKy+/sEqlfZJjRpYO3naqsvOvoeRaLfZRYT+20l6EaE9vwAs"
    "d4r7dM3hzSsqp8f5btAJdeohiytvdgdPnOrmldLY7aRNPDNLy2lTjdxpV3G+IIm3mW2sJa"
    "ikT5j7FeaRCu4kuJPgToI7Ce60L3dawKvxcKe0fO/5V+WORzMUlCdkqEOhUJvFbB2EFfBC"
    "ElUTnyJM9qJO3Y2T4K3Es7lQxjRQuAiSPFEN1VR0NWNJ2ZEmqlRmSb2ks3U51qyopa8gv0"
    "2IA4cVB5xgBS/L0yznFgeq8uzjKsNx98+I7X4SKEEp9qishHXPtVXXZYyrjAcuEmoxNBnE"
    "NReeiussPHv82srZxw2kf6Nnc/Xd0ZHklpW1kjYDmXO4p7TSrRKYBYk70QFZY/sDgHGnCE"
    "jWmP0lwHy1spYKILU62gufxkm3iGHwP2BH6QTHljD9El+NmFh5zKpIJKHzSIMDklI/hIEf"
    "Ad/5FGxxbS+pqXSBcZOg6iZFZyEqu2EVVTVZddJOxnTQp6Epkx/gD8WxUb+jaRXaKoMVHA"
    "tMcCFXB/xy69oK82VENqhfxkpr7WE4RMPfMH74m8hkEWqsUGOFGivU2E7U2JebeJ33T2Qu"
    "SyZxaYi8qgDRVt2UDFgey13sEhctE+gqg0ygq7UyATpVVBrhhTmQT8sPC/n4u+aarG8She"
    "pENhlghaVqccXniokuq3XgA58rykAZ9S7ikuOwJEsYoBZrgGhHXlSlddUjnRkMoCITo9q4"
    "kZiaU3MYzYNnB1x6bFq+97pLgqrpLoihHQaoG87gWBvhcK+aKlWOXJQpDgyYbtq76ZqBAz"
    "ga6tccEw5hNVty0+9TQ5fSNoSjv+tYYAyB44XA5mqFSZveK/J0YuPEuCmCV50Ms7PzNrOF"
    "5zhViyCeB8ESWH5Nc0HaFaCeQ8NDVfD6LDAy2qBPYQU2Ndtt0iu4afD5zc0VNSo/vyyGHj"
    "9fn19AH2APwEJeLFaWKzeEz7bsRUXHtwv1zOyIoGekuAFzw50oaTR4ahoabkbkgWFuua73"
    "yI95Zja0ig77RytrYgy84AYehhhzA8RuGJIDRBD+wGFNUgVl1S4po4EE5QxZwdEkyyDJYo"
    "8BuhikDiJ0JeH+ZaG6M15H1ab9A3b2wls6YeWghCMM9drAbhtzIsbWsL+raIivLf/pLkCf"
    "jNUZrTL1KVjupcXuPwuNUu7IJad0E36aUwe2wKZs8A0+qqo2fspZIfZGPnOI6iBwZjmuaY"
    "zNDULskwfwhFtSaIRAT96MzGXJ6UKQLikVLeDP+0XqsPjkDP5n7csFj89KfnhujDVmC4VV"
    "hBnJRcTqI4zo2ZjjilzLgrVYr0qE+kSoT4T6RKhPhPrEfl0t9zY6iO72upa9zScEtO6ADp"
    "L+73v2A3ekmrDpH21dV7T9V1voPhJifYXDgIplaht2QMsselfmtamCFrCQbMYkwMK8K01j"
    "mXilafUzr9C5V6mNEaP7XCc7ihBWUm9YdIZlcN8y1RVRpKvg/tjNQQ50S0mBCsWjPaQ6wO"
    "Mu3YvqqA2krKIuyNZAh+hwCS6lJSeI3WKqAU3X9GZdeqL/hOpDrOr9/IqVqkyLqlKquqqm"
    "4z2Uqky0qRCqZhj0GqkKFUAzKcoaVWbKJVHVTUXowunJPATGCRtdEg7TmCIvA4BzCAH94u"
    "Q14TB+Lzw2q+vTOSCEd9mdnxrHlYDX/zsVStTF1giUSe/brE/O0p6eV6PUVZTEobqajaQA"
    "gHKSXKfufW2zQRcSLIlzlp12CKVSDaeE4ikUT6F4CsVTKJ6dKJ55S0u7+nZlLZe1WZ+51f"
    "HYeK1fie7LsA30Uhvm/A2aGYlyhlSggB4WiyDusoRtvfxZMBuAJkeODRScbOiy6nPHVkC9"
    "ivnlDcng6wPqdIy90OUvJ21XSOpe9sQjNDhM5ZscQlv1LH+iMfP3Z+nNDEL87G33uSFoct"
    "1mqlVvHsedp8axfdwQMOx4p7ij7VCdKTQ13DZVb3aQ20wk42W3O3Ol2LaTcICYZS+IqCCi"
    "gogKIipm2ddHQFrtGKGwbBmn1O8Zp5Q2jcMdFweqafm+05lITPO1CYaBaSO3b1gNsgNu3+"
    "kkZBJiTmp/IMLEkeDQ2TyBPFTUPvp6/Chc/9HXuhBcHtUuR193hN+o4Gzr6Gt5aEFMYWjn"
    "c97ZN69mgkjpwVm9Xz0LpKoSEFNJ2k8SYYvAxkk9NTw1y/ipJ6p5chEfST3Jrt0+4Mq/1a"
    "HgsoLLCi4ruKzgsp1x2Shtz1m5QWYwADY7n7vIi3FeF0BDClm1BxNHeR1J5NQCF44r43x9"
    "lGmqqaxra3UXq34doakOkqNFmOrAyebjlxGyKqztXUEIyqt/17OCwrrjrPSAzK81HdxQKG"
    "4J/8aCLNQhy4gtsIfkbuPaWKAP1LlKppHscCi2BRS0QtAKQSsEreiEVtROtmqYkZqb9L45"
    "YH0v1hubePFb2YmN64ZC6Ya7Zl5xuLYHysVL9Ix13pJQKd8I93wdDIz7VJ2jAIkiaWPl9H"
    "GsnuJoCdpiCDj6ZKxRv+Ue8sThWK7sk//c3nysCSIn5QsO+OxDbP5wPDsanyy9TfTnkZsh"
    "XdanmCxq6cLLuhLvfdOquUE4NDc3xZal0OeiCxSbG5rxsNIO2mqIokfOAw/PQUrzwPnApI"
    "wGsiDnQfbU6lZRSupgB6JSy1nDPVfZ3Ut0Ui9rtbRUrsQd4BqvYdDD7nnH2RGuiDP1Hh9U"
    "wct9NbeWqQ9oZ/GvOJG8Bef5FXvyGC8z4lhmgkXoTAGoFzoJiHYLnYSHeIVO1dWmeIeR0j"
    "7FjQVZhM50CFszL11kQAipUkiVQqoUUmUnUmVtL/0e2N7KWla7mrAqujk2e5uYH9vJ9f0S"
    "d6P5/uLd5fXZ1ZuJOdYL20mk5FaVijrlVyv08HPx4UmaDQtQTXFirdLsH9yFt4mC8IlHhi"
    "FMBqbEaIoZDyVlEthMHFZQ1rBuKtNYoUE72KDtH82piQiCjEVjvM+5ChQLiZoArapg2bBP"
    "0x0VlbHRupKmqXclKR9E46EHe6zjNdrquOO2A9KELkQIHhrHELBKORqfXMG+NuCwHLCTR9"
    "MVj4FId5HeUrcjQkEb2s33vLQkN9mrUyUaC7bYMUHwOsHrBK8TvE7wutcyS3uv5UrbTdKe"
    "SBJDIgosVb9XglTiIP+EHAjdkC28iSYaQ02m07FySv5EnEN2cIiedJYBHAXZai6O1tPZrk"
    "6y4+xYL1nht1e21LGR/XXMbKYT1Rmbp3QWgQpQldA1lJavK9JkPD311uXDx08QsPF8Sc59"
    "2jOT3vOTqNduYqK1ZedzRD410yjv2I48NqHyltCE0D3e0T5mpJdoT8tl5tuTnqGFaamK/c"
    "1aQo7TDUa/4mu9CojEugZl+nf01cWb1jWg1m7nWtqgYvHxLlYXjwflLIw/eU3qOX/+Hu1m"
    "/d/yspy8P8/J28H76YL8s1nsBfR1SQTA0d76M0IvEHqB0AuEXiD0gi70gnXofUVeS8bxzH"
    "MsaLP+Z8UbU3uCOiRLi0NpZxe39FSL4U6vWG/nS8/m9gBl1b8DtIluxw4YJsorH6wC37N5"
    "MCZtBoCwbE3x8g8SXmzPeXEVPRvUMQslqUH/4E9Vl5E5HmFWXAhWVvjAg2Ru0bvipE3Rap"
    "G6DVgX0jjCLEMx40RMingRkyL6WW/jDISevRhV6BLJmXGTIGHlZXYJESn8+6yyx6UF1G6c"
    "U/kyV4RpEgceQFyrx6A6iCFPVEM1FV3NIhnZkaZwRhrJqKf+X0G44VxClzDpuctmR/Hw3Q"
    "t6NThATIq/TAAPEnytjbHVJ4DWx9j2SQDtAdZjZGS2yiJs2708/x/0Rhnv"
)
