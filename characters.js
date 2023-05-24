var data = {
    "carray": [
        ["amaria", "a", 2],
        ["amaria", "b", 2],
        ["brenda", "a", 2],
        ["brenda", "b", 2],
        ["cornelia", "a", 2],
        ["cornelia", "b", 2],
        ["erica", "a", 3],
        ["erica", "b", 3],
        ["erica", "c", 3],
        ["iroha", "a", 2],
        ["iroha", "b", 2],
        ["izuna", "a", 5],
        ["izuna", "aears", 5],
        ["izuna", "b", 5],
        ["izuna", "bears", 5],
        ["izuna", "sword", 5],
        ["marin", "a", 3],
        ["marin", "b", 3],
        ["marin", "c", 3],
        ["phila", "a", 2],
        ["phila", "b", 2],
        ["sadie", "a", 1],
        ["tori", "a", 2],
        ["tori", "b", 2],
        ["watson", "a", 2],
        ["watson", "b", 2],
    ],
    "characters": {
        "amaria": {
            "name": "amaria",
            "poses": {
                "a": {
                    "default_outfit": "uniform/uniform.png",
                    "default_accessories": [
                        ["uniform/hair+1/off.png", "+1", 111],
                        ["acc_bracelets/off.png", "0", 160],
                    ],
                    "default_left_crop": 170,
                    "default_right_crop": 446,
                    "default_top_crop": 28,
                    "max_face_height": 205,
                    "pose_path": "characters/amaria/a/", //Saves some characters
                    "faces": {
                        //Put all face variations (Blushes + mutation + any accessories variation) in here
                        "face": ["0.png", "1.png"], //Default face + Blush
                        "blush": ["0.png", "1.png"],
                        "face/makeup": [], // Default accessories
                        "blush/makeup": [],
                        "mutations/twintails/face": [], //Any mutations
                        "mutations/twintails/blush": [],
                        "mutations/twintails/face/makeup": [], //Any accessories in mutations
                        "mutations/twintails/blush/makeup": [],
                    },
                    //List of accessory names for sprite viewer
                    "accessories": ["hair", "bracelets", "makeup"],
                    //Failure procedure:
                    /*
                    Go down list until an matching path is found
                    Rules: Never check blush unless blush is chosen first

                    1. If blush, check without blush. mutations/twintails/blush/makeup -> mutations/twintails/face/makeup
                    2. Check without accessory. mutations/twintails/face/makeup -> mutations/twintails/face
                    3. If using a mutation, check the default face, with accessory if available. mutations/twintails/face/makeup -> face/makeup
                    4. If all else fails, use a default false. face/makeup -> face

                    */
                    //The adding string to find the proper path would be
                    // pose_path + "faces" + ("mutations" + mutation(twintails) or nothing) + face_state (blush or face) +  accessory if applicable)
                    "outfits": [
                        [
                            "casual/casual.png", //Outfit path
                            "face", //face pointer (Match what is in faces)
                            [
                                //Accessories now have 5 columns. Accessory name, state, path, layer, scaling (This only applies to outfits that are off)
                                ["hair", "off", "uniform/hair+1/off.png", "+1", 111], //real_name, state, path, layering, default scaling (Only for default accessories)
                                ["bracelets", "off", "acc_bracelets/off.png", "0", 160],
                                ["bracelets", "on", "acc_bracelets/on.png", "0", 0],
                                ["hair", "on_ponytail", "acc_hair+1/on_ponytail.png", "+1", 0],
                            ],
                        ],
                        [
                            "casual/casual2.png",
                            "mutations/twintails",
                            [
                                ["hair", "uniform/hair+1/off.png", "+1", 111],
                                ["bracelets", "acc_bracelets/off.png", "0", 160],
                            ],
                        ],
                    ],
                },
                "b": {
                    "max_face_height": 205,
                    "face_path": "characters/amaria/b/faces/face/",
                    "faces": ["0.png", "1.png"],
                    "outfit_path": "characters/amaria/b/outfits/",
                    "default_outfit": "uniform/uniform.png",
                    "default_accessories": [["uniform/hair+1/off.png", "+1", 111]],
                    "default_left_crop": 255,
                    "default_right_crop": 446,
                    "default_top_crop": 28,
                    "outfits": [
                        ["casual/casual.png", [["uniform/hair+1/off.png", "+1", 111]]],
                        ["casual_book/casual_book.png", [["uniform/hair+1/off.png", "+1", 111]]],
                        ["gym/gym.png", [["uniform/hair+1/off.png", "+1", 111]]],
                        ["nude/nude.png", [["uniform/hair+1/off.png", "+1", 111]]],
                        ["uniform/uniform.png", [["uniform/hair+1/off.png", "+1", 111]]],
                    ],
                },
            },
        },
        "brenda": {
            "name": "brenda",
            "poses": {
                "a": {
                    "max_face_height": 261,
                    "face_path": "characters/brenda/a/faces/face/",
                    "faces": ["0.webp", "1.webp", "2.webp", "3.webp", "4.webp", "5.webp", "6.webp", "7.webp"],
                    "outfit_path": "characters/brenda/a/outfits/",
                    "default_outfit": "uniform.webp",
                    "default_accessories": [],
                    "default_left_crop": 166,
                    "default_right_crop": 389,
                    "default_top_crop": 54,
                    "outfits": [
                        ["dress.webp", []],
                        ["gothloli.webp", []],
                        ["suit.webp", []],
                        ["uniform.webp", []],
                    ],
                },
                "b": {
                    "max_face_height": 270,
                    "face_path": "characters/brenda/b/faces/face/",
                    "faces": ["0.webp", "1.webp", "2.webp", "3.webp", "4.webp", "5.webp", "6.webp"],
                    "outfit_path": "characters/brenda/b/outfits/",
                    "default_outfit": "uniform.webp",
                    "default_accessories": [],
                    "default_left_crop": 183,
                    "default_right_crop": 439,
                    "default_top_crop": 62,
                    "outfits": [
                        ["dress.webp", []],
                        ["gothloli.webp", []],
                        ["suit.webp", []],
                        ["uniform.webp", []],
                    ],
                },
            },
        },
        "cornelia": {
            "name": "cornelia",
            "poses": {
                "a": {
                    "max_face_height": 201,
                    "face_path": "characters/cornelia/a/faces/face/",
                    "faces": [
                        "0.webp",
                        "1.webp",
                        "2.webp",
                        "3.webp",
                        "4.webp",
                        "5.webp",
                        "6.webp",
                        "7.webp",
                        "8.webp",
                        "9.webp",
                        "10.webp",
                        "11.webp",
                        "12.webp",
                        "13.webp",
                        "14.webp",
                        "15.webp",
                        "16.webp",
                        "17.webp",
                        "18.webp",
                        "19.webp",
                        "20.webp",
                        "21.webp",
                        "22.webp",
                    ],
                    "outfit_path": "characters/cornelia/a/outfits/",
                    "default_outfit": "gym2.webp",
                    "default_accessories": [],
                    "default_left_crop": 70,
                    "default_right_crop": 363,
                    "default_top_crop": 6,
                    "outfits": [
                        ["gym.webp", []],
                        ["gym2.webp", []],
                    ],
                },
                "b": {
                    "max_face_height": 217,
                    "face_path": "characters/cornelia/b/faces/mutations/",
                    "faces": [
                        "twintails/face/0.webp",
                        "twintails/face/1.webp",
                        "twintails/face/2.webp",
                        "twintails/face/3.webp",
                        "twintails/face/4.webp",
                        "twintails/face/5.webp",
                        "twintails/face/6.webp",
                        "twintails/face/7.webp",
                        "twintails/face/8.webp",
                        "twintails/face/9.webp",
                        "twintails/face/10.webp",
                        "twintails/face/11.webp",
                        "twintails/face/12.webp",
                        "twintails/face/13.webp",
                        "twintails/face/14.webp",
                        "twintails/face/15.webp",
                        "twintails/face/16.webp",
                        "twintails/face/17.webp",
                        "twintails/face/18.webp",
                        "twintails/face/19.webp",
                        "twintails/face/20.webp",
                        "twintails/face/21.webp",
                        "twintails/face/22.webp",
                        "twintails/face/23.webp",
                        "twintails/face/24.webp",
                        "twintails/face/25.webp",
                        "twintails/face/26.webp",
                        "twintails/face/27.webp",
                        "twintails/face/28.webp",
                        "twintails/face/29.webp",
                        "twintails/face/30.webp",
                        "twintails/face/31.webp",
                        "twintails/face/32.webp",
                        "twintails/face/33.webp",
                        "twintails/face/34.webp",
                    ],
                    "outfit_path": "characters/cornelia/b/outfits/",
                    "default_outfit": "uniform/uniform.webp",
                    "default_accessories": [["uniform/ponytail/off.webp", "0", 200]],
                    "default_left_crop": 14,
                    "default_right_crop": 425,
                    "default_top_crop": 14,
                    "outfits": [["uniform/uniform.webp", [["uniform/ponytail/off.webp", "0", 200]]]],
                },
            },
        },
        "erica": {
            "name": "erica",
            "poses": {
                "a": {
                    "max_face_height": 251,
                    "face_path": "characters/erica/a/faces/face/",
                    "faces": [
                        "0.webp",
                        "1.webp",
                        "2.webp",
                        "3.webp",
                        "4.webp",
                        "5.webp",
                        "6.webp",
                        "7.webp",
                        "8.webp",
                        "9.webp",
                        "10.webp",
                        "11.webp",
                        "12.webp",
                        "13.webp",
                        "14.webp",
                        "15.webp",
                        "16.webp",
                        "17.webp",
                        "18.webp",
                        "19.webp",
                        "20.webp",
                        "21.webp",
                        "22.webp",
                        "23.webp",
                        "24.webp",
                        "25.webp",
                        "26.webp",
                        "27.webp",
                    ],
                    "outfit_path": "characters/erica/a/outfits/",
                    "default_outfit": "uniform/uniform.webp",
                    "default_accessories": [],
                    "default_left_crop": 100,
                    "default_right_crop": 329,
                    "default_top_crop": 0,
                    "outfits": [
                        ["casual/casual.webp", []],
                        ["gown/gown.webp", []],
                        ["kimono/kimono.webp", []],
                        ["traditional/traditional.webp", []],
                        ["uniform/uniform.webp", []],
                        ["uniform_b/uniform_b.webp", []],
                        ["uniform_c/uniform_c.webp", []],
                    ],
                },
                "b": {
                    "max_face_height": 243,
                    "face_path": "characters/erica/b/faces/face/",
                    "faces": [
                        "0.webp",
                        "1.webp",
                        "2.webp",
                        "3.webp",
                        "4.webp",
                        "5.webp",
                        "6.webp",
                        "7.webp",
                        "8.webp",
                        "9.webp",
                        "10.webp",
                        "11.webp",
                        "12.webp",
                        "13.webp",
                        "14.webp",
                        "15.webp",
                        "16.webp",
                        "17.webp",
                        "18.webp",
                        "19.webp",
                        "20.webp",
                        "21.webp",
                        "22.webp",
                        "23.webp",
                        "24.webp",
                        "25.webp",
                        "26.webp",
                        "27.webp",
                    ],
                    "outfit_path": "characters/erica/b/outfits/",
                    "default_outfit": "uniform.webp",
                    "default_accessories": [],
                    "default_left_crop": 71,
                    "default_right_crop": 326,
                    "default_top_crop": 0,
                    "outfits": [
                        ["casual.webp", []],
                        ["gown.webp", []],
                        ["kimono.webp", []],
                        ["traditional.webp", []],
                        ["uniform.webp", []],
                        ["uniform_b.webp", []],
                        ["uniform_c.webp", []],
                    ],
                },
                "c": {
                    "max_face_height": 240,
                    "face_path": "characters/erica/c/faces/face/",
                    "faces": [
                        "0.webp",
                        "1.webp",
                        "2.webp",
                        "3.webp",
                        "4.webp",
                        "5.webp",
                        "6.webp",
                        "7.webp",
                        "8.webp",
                        "9.webp",
                        "10.webp",
                        "11.webp",
                        "12.webp",
                        "13.webp",
                        "14.webp",
                        "15.webp",
                        "16.webp",
                        "17.webp",
                        "18.webp",
                        "19.webp",
                        "20.webp",
                        "21.webp",
                        "22.webp",
                        "23.webp",
                        "24.webp",
                        "25.webp",
                        "26.webp",
                        "27.webp",
                    ],
                    "outfit_path": "characters/erica/c/outfits/",
                    "default_outfit": "casual.webp",
                    "default_accessories": [],
                    "default_left_crop": 140,
                    "default_right_crop": 431,
                    "default_top_crop": 6,
                    "outfits": [
                        ["casual.webp", []],
                        ["gown.webp", []],
                        ["kimono.webp", []],
                        ["traditional.webp", []],
                        ["uniform_c.webp", []],
                    ],
                },
            },
        },
        "iroha": {
            "name": "iroha",
            "poses": {
                "a": {
                    "max_face_height": 211,
                    "face_path": "characters/iroha/a/faces/face/",
                    "faces": ["0.webp", "1.webp", "2.webp", "3.webp", "4.webp", "5.webp", "6.webp", "7.webp"],
                    "outfit_path": "characters/iroha/a/outfits/",
                    "default_outfit": "uniform.webp",
                    "default_accessories": [],
                    "default_left_crop": 105,
                    "default_right_crop": 327,
                    "default_top_crop": 31,
                    "outfits": [
                        ["casual.webp", []],
                        ["maid.webp", []],
                        ["uniform.webp", []],
                        ["uniform_b.webp", []],
                    ],
                },
                "b": {
                    "max_face_height": 215,
                    "face_path": "characters/iroha/b/faces/face/",
                    "faces": ["0.webp", "1.webp", "2.webp", "3.webp", "4.webp", "5.webp", "6.webp", "7.webp"],
                    "outfit_path": "characters/iroha/b/outfits/",
                    "default_outfit": "uniform.webp",
                    "default_accessories": [],
                    "default_left_crop": 182,
                    "default_right_crop": 407,
                    "default_top_crop": 28,
                    "outfits": [
                        ["casual.webp", []],
                        ["maid.webp", []],
                        ["uniform.webp", []],
                        ["uniform_b.webp", []],
                    ],
                },
            },
        },
        "izuna": {
            "name": "izuna",
            "poses": {
                "a": {
                    "max_face_height": 220,
                    "face_path": "characters/izuna/a/faces/face/",
                    "faces": ["0.webp", "1.webp", "2.webp", "3.webp", "4.webp", "5.webp", "6.webp", "7.webp", "8.webp"],
                    "outfit_path": "characters/izuna/a/outfits/",
                    "default_outfit": "uniform.webp",
                    "default_accessories": [],
                    "default_left_crop": 222,
                    "default_right_crop": 482,
                    "default_top_crop": 26,
                    "outfits": [
                        ["casual.webp", []],
                        ["casualb.webp", []],
                        ["casualbb.webp", []],
                        ["gym.webp", []],
                        ["uniform.webp", []],
                        ["uniforms.webp", []],
                        ["uniformsnoband.webp", []],
                    ],
                },
                "aears": {
                    "max_face_height": 220,
                    "face_path": "characters/izuna/aears/faces/face/",
                    "faces": ["0.webp", "1.webp", "2.webp", "3.webp", "4.webp", "5.webp", "6.webp", "7.webp", "8.webp"],
                    "outfit_path": "characters/izuna/aears/outfits/",
                    "default_outfit": "casualb.webp",
                    "default_accessories": [],
                    "default_left_crop": 210,
                    "default_right_crop": 483,
                    "default_top_crop": 15,
                    "outfits": [
                        ["casualb.webp", []],
                        ["casualbb.webp", []],
                    ],
                },
                "b": {
                    "max_face_height": 210,
                    "face_path": "characters/izuna/b/faces/face/",
                    "faces": ["0.webp", "1.webp", "2.webp", "3.webp", "4.webp", "5.webp"],
                    "outfit_path": "characters/izuna/b/outfits/",
                    "default_outfit": "uniform.webp",
                    "default_accessories": [],
                    "default_left_crop": 204,
                    "default_right_crop": 461,
                    "default_top_crop": 14,
                    "outfits": [
                        ["casual.webp", []],
                        ["casualb.webp", []],
                        ["uniform.webp", []],
                    ],
                },
                "bears": {
                    "max_face_height": 210,
                    "face_path": "characters/izuna/bears/faces/face/",
                    "faces": ["0.webp", "1.webp", "2.webp", "3.webp", "4.webp", "5.webp"],
                    "outfit_path": "characters/izuna/bears/outfits/",
                    "default_outfit": "casualb.webp",
                    "default_accessories": [],
                    "default_left_crop": 204,
                    "default_right_crop": 461,
                    "default_top_crop": 14,
                    "outfits": [["casualb.webp", []]],
                },
                "sword": {
                    "max_face_height": 220,
                    "face_path": "characters/izuna/sword/faces/face/",
                    "faces": ["0.webp", "1.webp", "2.webp", "3.webp", "4.webp", "5.webp"],
                    "outfit_path": "characters/izuna/sword/outfits/",
                    "default_outfit": "uniform.webp",
                    "default_accessories": [],
                    "default_left_crop": 210,
                    "default_right_crop": 483,
                    "default_top_crop": 15,
                    "outfits": [["uniform.webp", []]],
                },
            },
        },
        "marin": {
            "name": "marin",
            "poses": {
                "a": {
                    "max_face_height": 456,
                    "face_path": "characters/marin/a/faces/face/",
                    "faces": [
                        "0.webp",
                        "1.webp",
                        "2.webp",
                        "3.webp",
                        "4.webp",
                        "5.webp",
                        "6.webp",
                        "7.webp",
                        "8.webp",
                        "9.webp",
                        "10.webp",
                        "11.webp",
                        "12.webp",
                        "13.webp",
                        "14.webp",
                        "15.webp",
                        "16.webp",
                    ],
                    "outfit_path": "characters/marin/a/outfits/",
                    "default_outfit": "casual.webp",
                    "default_accessories": [],
                    "default_left_crop": 162,
                    "default_right_crop": 543,
                    "default_top_crop": 126,
                    "outfits": [
                        ["bathrobe.webp", []],
                        ["casual.webp", []],
                        ["fashion.webp", []],
                        ["magical.webp", []],
                        ["pj.webp", []],
                        ["swimsuit2.webp", []],
                    ],
                },
                "b": {
                    "max_face_height": 456,
                    "face_path": "characters/marin/b/faces/face/",
                    "faces": [
                        "0.webp",
                        "1.webp",
                        "2.webp",
                        "3.webp",
                        "4.webp",
                        "5.webp",
                        "6.webp",
                        "7.webp",
                        "8.webp",
                        "9.webp",
                        "10.webp",
                        "11.webp",
                        "12.webp",
                        "13.webp",
                        "14.webp",
                        "15.webp",
                        "16.webp",
                    ],
                    "outfit_path": "characters/marin/b/outfits/",
                    "default_outfit": "casual.webp",
                    "default_accessories": [],
                    "default_left_crop": 162,
                    "default_right_crop": 543,
                    "default_top_crop": 126,
                    "outfits": [
                        ["casual.webp", []],
                        ["fashion.webp", []],
                        ["magical.webp", []],
                        ["pj.webp", []],
                        ["swimsuit2.webp", []],
                    ],
                },
                "c": {
                    "max_face_height": 456,
                    "face_path": "characters/marin/c/faces/face/",
                    "faces": [
                        "0.webp",
                        "1.webp",
                        "2.webp",
                        "3.webp",
                        "4.webp",
                        "5.webp",
                        "6.webp",
                        "7.webp",
                        "8.webp",
                        "9.webp",
                        "10.webp",
                        "11.webp",
                        "12.webp",
                        "13.webp",
                        "14.webp",
                        "15.webp",
                        "16.webp",
                    ],
                    "outfit_path": "characters/marin/c/outfits/",
                    "default_outfit": "casual.webp",
                    "default_accessories": [],
                    "default_left_crop": 162,
                    "default_right_crop": 543,
                    "default_top_crop": 126,
                    "outfits": [
                        ["casual.webp", []],
                        ["fashion.webp", []],
                        ["magical.webp", []],
                        ["pj.webp", []],
                        ["swimsuit2.webp", []],
                    ],
                },
            },
        },
        "phila": {
            "name": "phila",
            "poses": {
                "a": {
                    "max_face_height": 171,
                    "face_path": "characters/phila/a/faces/face/",
                    "faces": [
                        "0.webp",
                        "1.webp",
                        "2.webp",
                        "3.webp",
                        "4.webp",
                        "5.webp",
                        "6.webp",
                        "7.webp",
                        "8.webp",
                        "9.webp",
                    ],
                    "outfit_path": "characters/phila/a/outfits/",
                    "default_outfit": "uniform.webp",
                    "default_accessories": [],
                    "default_left_crop": 26,
                    "default_right_crop": 292,
                    "default_top_crop": 0,
                    "outfits": [
                        ["dress.webp", []],
                        ["swimsuit.webp", []],
                        ["uniform.webp", []],
                    ],
                },
                "b": {
                    "max_face_height": 171,
                    "face_path": "characters/phila/b/faces/face/",
                    "faces": ["0.webp", "1.webp", "2.webp", "3.webp", "4.webp", "5.webp", "6.webp", "7.webp", "8.webp"],
                    "outfit_path": "characters/phila/b/outfits/",
                    "default_outfit": "uniform.webp",
                    "default_accessories": [],
                    "default_left_crop": 91,
                    "default_right_crop": 306,
                    "default_top_crop": 5,
                    "outfits": [
                        ["dress.webp", []],
                        ["gym.webp", []],
                        ["uniform.webp", []],
                    ],
                },
            },
        },
        "sadie": {
            "name": "sadie",
            "poses": {
                "a": {
                    "max_face_height": 269,
                    "face_path": "characters/sadie/a/faces/face/",
                    "faces": [
                        "0.webp",
                        "1.webp",
                        "2.webp",
                        "3.webp",
                        "4.webp",
                        "5.webp",
                        "6.webp",
                        "7.webp",
                        "8.webp",
                        "9.webp",
                        "10.webp",
                        "11.webp",
                        "12.webp",
                        "13.webp",
                        "14.webp",
                        "15.webp",
                        "16.webp",
                        "17.webp",
                        "18.webp",
                        "19.webp",
                        "20.webp",
                        "21.webp",
                        "22.webp",
                        "23.webp",
                        "24.webp",
                        "25.webp",
                        "26.webp",
                        "27.webp",
                        "28.webp",
                        "29.webp",
                        "30.webp",
                        "31.webp",
                        "32.webp",
                    ],
                    "outfit_path": "characters/sadie/a/outfits/",
                    "default_outfit": "uniform/uniform.webp",
                    "default_accessories": [["uniform/hairdown/off.webp", "0", 200]],
                    "default_left_crop": 0,
                    "default_right_crop": 428,
                    "default_top_crop": 0,
                    "outfits": [
                        ["casual/casual.webp", [["uniform_madie/hairdown/off.webp", "0", 200]]],
                        ["casual_b/casual_b.webp", [["uniform_madie/hairdown/off.webp", "0", 200]]],
                        ["casual_madie/casual.webp", [["uniform_madie/hairdown/off.webp", "0", 200]]],
                        ["casual_madie_b/casual_b.webp", [["uniform_madie/hairdown/off.webp", "0", 200]]],
                        ["cheer.webp", [["uniform_madie/hairdown/off.webp", "0", 200]]],
                        ["cheer_inverted.webp", [["uniform_madie/hairdown/off.webp", "0", 200]]],
                        ["cheer_madie.webp", [["uniform_madie/hairdown/off.webp", "0", 200]]],
                        ["cheer_madie_inverted.webp", [["uniform_madie/hairdown/off.webp", "0", 200]]],
                        ["sleepwear/sleepwear.webp", [["uniform_madie/hairdown/off.webp", "0", 200]]],
                        ["sleepwear_madie/sleepwear.webp", [["uniform_madie/hairdown/off.webp", "0", 200]]],
                        ["uniform/uniform.webp", [["uniform_madie/hairdown/off.webp", "0", 200]]],
                        ["uniform_madie/uniform_madie.webp", [["uniform_madie/hairdown/off.webp", "0", 200]]],
                    ],
                },
            },
        },
        "tori": {
            "name": "tori",
            "poses": {
                "a": {
                    "max_face_height": 236,
                    "face_path": "characters/tori/a/faces/face/",
                    "faces": [
                        "0.webp",
                        "1.webp",
                        "2.webp",
                        "3.webp",
                        "4.webp",
                        "5.webp",
                        "6.webp",
                        "7.webp",
                        "8.webp",
                        "9.webp",
                        "10.webp",
                        "11.webp",
                        "12.webp",
                        "13.webp",
                        "14.webp",
                        "15.webp",
                    ],
                    "outfit_path": "characters/tori/a/outfits/",
                    "default_outfit": "uniform.webp",
                    "default_accessories": [],
                    "default_left_crop": 95,
                    "default_right_crop": 306,
                    "default_top_crop": 0,
                    "outfits": [
                        ["casual.webp", []],
                        ["fancy.webp", []],
                        ["gym.webp", []],
                        ["uniform.webp", []],
                    ],
                },
                "b": {
                    "max_face_height": 238,
                    "face_path": "characters/tori/b/faces/face/",
                    "faces": [
                        "0.webp",
                        "1.webp",
                        "2.webp",
                        "3.webp",
                        "4.webp",
                        "5.webp",
                        "6.webp",
                        "7.webp",
                        "8.webp",
                        "9.webp",
                        "10.webp",
                        "11.webp",
                        "12.webp",
                        "13.webp",
                    ],
                    "outfit_path": "characters/tori/b/outfits/",
                    "default_outfit": "uniform.webp",
                    "default_accessories": [],
                    "default_left_crop": 95,
                    "default_right_crop": 417,
                    "default_top_crop": 17,
                    "outfits": [
                        ["casual.webp", []],
                        ["formal.webp", []],
                        ["swimsuit.webp", []],
                        ["uniform.webp", []],
                    ],
                },
            },
        },
        "watson": {
            "name": "watson",
            "poses": {
                "a": {
                    "max_face_height": 250,
                    "face_path": "characters/watson/a/faces/face/",
                    "faces": ["0.webp", "1.webp", "2.webp", "3.webp", "4.webp", "5.webp", "6.webp"],
                    "outfit_path": "characters/watson/a/outfits/",
                    "default_outfit": "coat.webp",
                    "default_accessories": [],
                    "default_left_crop": 156,
                    "default_right_crop": 373,
                    "default_top_crop": 2,
                    "outfits": [
                        ["coat.webp", []],
                        ["coat_glasses.webp", []],
                    ],
                },
                "b": {
                    "max_face_height": 789,
                    "face_path": "characters/watson/b/faces/face/",
                    "faces": ["0.webp"],
                    "outfit_path": "characters/watson/b/outfits/",
                    "default_outfit": "mask.webp",
                    "default_accessories": [],
                    "default_left_crop": 77,
                    "default_right_crop": 609,
                    "default_top_crop": 1,
                    "outfits": [["mask.webp", []]],
                },
            },
        },
    },
};
