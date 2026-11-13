def test_el_paquete_se_importa():
    import ia_local

    assert ia_local.__version__ == "1.0.0"
