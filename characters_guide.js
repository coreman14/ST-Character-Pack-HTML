var data = {
    "carray": [
        ["amaria", "a", 2],
        ["amaria", "b", 2],
    ],
    "characters": {
        "amaria": {
            "name": "amaria",
            "poses": {
                "a": {
                    "default_outfit": "uniform/uniform.png",
                    "default_faces": "face", //To assign the correct faces to the default
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
                    "accessories": [
                        ["hair", "acc"],
                        ["bracelets", "acc"],
                        ["makeup", "face"],
                    ],
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
    },
};
