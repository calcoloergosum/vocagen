"""Check availability of resources required for the backend."""
from .. import resource_util


def main():
    for L1, L2_2_sentences in resource_util.L1_2_L2_2sentences.items():
        for L2, sentences in L2_2_sentences.items():
            check_resource(L1, L2, sentences)


def check_resource(L1, L2, sentences):
    root = resource_util.langpair2root[L1][L2]
    n_image_exists = 0
    n_image_watercolor_exists = 0
    n = 0
    
    ids_L1 = set()
    ids_L2 = set()
    for s_L2, s_L1 in sentences.items():
        id_L1 = resource_util.sentence2id(s_L1)
        id_L2 = resource_util.sentence2id(s_L2)

        ids_L1.add(id_L1)
        ids_L2.add(id_L2)

    if L1 == "en":
        ids = ids_L1
    elif L2 == "en":
        ids = ids_L2
    else:
        raise NotImplementedError(f"Unsupported language pair {L1} -> {L2} (Should include English).")

    images = set(p.stem for p in (root / "image").glob("*.png"))
    images_vertical = set(p.stem for p in (root / "image_watercolor").glob("*.png"))
    audios = set(p.stem.split("_")[0] for p in (root / "audio").glob("*.mp3"))

    print("#" * 80)
    print("L1:", L1)
    print("L2:", L2)
    print("n_sentence_L1:", len(ids_L1))
    print("n_sentence_L2:", len(ids_L2))
    print("n_image_horizontal:",         len(images))
    print("n_image_horizontal_known:",   len(ids & images))
    print("n_image_horizontal_missing:", len(ids - images))
    print("n_image_horizontal_orphan:",  len(images - ids))
    print("n_image_vertical:",           len(ids & images_vertical))
    print("n_image_vertical_missing:",   len(ids - images_vertical))
    print("n_image_vertical_orphan:",    len(images_vertical - ids))
    print("n_audio:", len(audios))
    print("n_audio_L1:", len(ids_L1 & audios))
    print("n_audio_L1_missing:", len(ids_L1 - audios))
    print("n_audio_L2:", len(ids_L2 & audios))
    print("n_audio_L2_missing:", len(ids_L2 - audios))


if __name__ == '__main__':
    main()
