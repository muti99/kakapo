"""Start Codon Context."""

contexts = {'1437180_L': ((0.3, 0.3, 0.28, 0.12),
                          (0.4, 0.28, 0.11, 0.22),
                          (0.52, 0.04, 0.34, 0.1),
                          (0.47, 0.22, 0.17, 0.14),
                          (0.24, 0.3, 0.23, 0.24),
                          (0.28, 0.16, 0.33, 0.23),
                          (0.22, 0.15, 0.28, 0.35),
                          (0.25, 0.14, 0.26, 0.35),
                          (0.29, 0.13, 0.2, 0.38),
                          (0.26, 0.18, 0.19, 0.37)),
            '1437180_R': ((0.06, 0.08, 0.74, 0.12),
                          (0.19, 0.59, 0.22, 0.0),
                          (0.23, 0.1, 0.37, 0.31),
                          (0.49, 0.18, 0.22, 0.11),
                          (0.22, 0.3, 0.24, 0.25),
                          (0.28, 0.31, 0.18, 0.23),
                          (0.23, 0.17, 0.34, 0.26),
                          (0.22, 0.26, 0.19, 0.33),
                          (0.19, 0.18, 0.25, 0.38),
                          (0.27, 0.19, 0.28, 0.26)),
            '3193_L': ((0.4, 0.34, 0.2, 0.06),
                       (0.48, 0.31, 0.14, 0.07),
                       (0.72, 0.08, 0.18, 0.02),
                       (0.44, 0.35, 0.12, 0.09),
                       (0.15, 0.39, 0.22, 0.23),
                       (0.23, 0.16, 0.41, 0.2),
                       (0.31, 0.26, 0.19, 0.23),
                       (0.18, 0.35, 0.18, 0.29),
                       (0.23, 0.31, 0.22, 0.24),
                       (0.34, 0.26, 0.19, 0.21)),
            '3193_R': ((0.14, 0.2, 0.56, 0.1),
                       (0.12, 0.58, 0.18, 0.12),
                       (0.15, 0.29, 0.29, 0.27),
                       (0.24, 0.2, 0.35, 0.21),
                       (0.26, 0.35, 0.14, 0.26),
                       (0.12, 0.41, 0.31, 0.16),
                       (0.32, 0.18, 0.35, 0.15),
                       (0.26, 0.32, 0.13, 0.29),
                       (0.13, 0.37, 0.28, 0.21),
                       (0.35, 0.19, 0.36, 0.1)),
            '33090_L': ((0.42, 0.27, 0.2, 0.11),
                        (0.42, 0.34, 0.09, 0.15),
                        (0.56, 0.08, 0.26, 0.1),
                        (0.44, 0.22, 0.18, 0.15),
                        (0.28, 0.3, 0.17, 0.25),
                        (0.33, 0.16, 0.25, 0.25),
                        (0.35, 0.2, 0.2, 0.25),
                        (0.32, 0.25, 0.17, 0.26),
                        (0.31, 0.21, 0.22, 0.27),
                        (0.34, 0.2, 0.21, 0.25)),
            '33090_R': ((0.15, 0.06, 0.67, 0.12),
                        (0.21, 0.54, 0.15, 0.1),
                        (0.19, 0.14, 0.35, 0.33),
                        (0.34, 0.15, 0.29, 0.22),
                        (0.24, 0.37, 0.18, 0.22),
                        (0.19, 0.3, 0.24, 0.27),
                        (0.3, 0.19, 0.28, 0.24),
                        (0.25, 0.31, 0.15, 0.29),
                        (0.24, 0.26, 0.23, 0.27),
                        (0.33, 0.19, 0.3, 0.17)),
            '4447_L': ((0.24, 0.41, 0.3, 0.04),
                       (0.26, 0.52, 0.12, 0.1),
                       (0.39, 0.1, 0.43, 0.08),
                       (0.34, 0.34, 0.22, 0.11),
                       (0.19, 0.41, 0.19, 0.21),
                       (0.25, 0.19, 0.35, 0.2),
                       (0.28, 0.26, 0.29, 0.17),
                       (0.28, 0.33, 0.22, 0.18),
                       (0.25, 0.26, 0.3, 0.19),
                       (0.25, 0.28, 0.28, 0.19)),
            '4447_R': ((0.13, 0.07, 0.71, 0.09),
                       (0.18, 0.6, 0.15, 0.07),
                       (0.11, 0.19, 0.52, 0.18),
                       (0.31, 0.19, 0.31, 0.19),
                       (0.23, 0.41, 0.21, 0.16),
                       (0.08, 0.45, 0.33, 0.14),
                       (0.3, 0.22, 0.3, 0.19),
                       (0.25, 0.33, 0.18, 0.24),
                       (0.11, 0.38, 0.36, 0.15),
                       (0.32, 0.22, 0.33, 0.14)),
            '58024_L': ((0.42, 0.27, 0.2, 0.11),
                        (0.42, 0.35, 0.08, 0.15),
                        (0.54, 0.09, 0.27, 0.1),
                        (0.44, 0.22, 0.19, 0.15),
                        (0.29, 0.3, 0.17, 0.25),
                        (0.34, 0.16, 0.25, 0.26),
                        (0.35, 0.2, 0.2, 0.26),
                        (0.33, 0.25, 0.17, 0.26),
                        (0.31, 0.2, 0.22, 0.27),
                        (0.34, 0.2, 0.21, 0.26)),
            '58024_R': ((0.15, 0.05, 0.68, 0.12),
                        (0.21, 0.54, 0.15, 0.1),
                        (0.19, 0.13, 0.35, 0.33),
                        (0.34, 0.15, 0.29, 0.22),
                        (0.24, 0.37, 0.19, 0.21),
                        (0.19, 0.29, 0.24, 0.28),
                        (0.29, 0.19, 0.27, 0.25),
                        (0.25, 0.31, 0.15, 0.29),
                        (0.25, 0.25, 0.23, 0.28),
                        (0.33, 0.19, 0.3, 0.18)),
            '71240_L': ((0.48, 0.22, 0.17, 0.13),
                        (0.47, 0.29, 0.07, 0.17),
                        (0.59, 0.08, 0.22, 0.11),
                        (0.48, 0.18, 0.18, 0.17),
                        (0.32, 0.26, 0.16, 0.26),
                        (0.37, 0.15, 0.21, 0.27),
                        (0.37, 0.18, 0.17, 0.28),
                        (0.35, 0.23, 0.15, 0.28),
                        (0.33, 0.19, 0.19, 0.29),
                        (0.37, 0.18, 0.18, 0.28)),
            '71240_R': ((0.15, 0.05, 0.68, 0.12),
                        (0.22, 0.52, 0.15, 0.11),
                        (0.22, 0.11, 0.29, 0.38),
                        (0.35, 0.14, 0.28, 0.23),
                        (0.24, 0.36, 0.18, 0.23),
                        (0.23, 0.25, 0.21, 0.32),
                        (0.29, 0.18, 0.26, 0.27),
                        (0.25, 0.3, 0.14, 0.3),
                        (0.29, 0.21, 0.19, 0.31),
                        (0.34, 0.18, 0.29, 0.19))}
