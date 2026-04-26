from quadra_diag.ml.catalog import DISEASE_SPECS
from quadra_diag.ml.training import train_model


def main() -> None:
    for disease in DISEASE_SPECS:
        train_model(disease)


if __name__ == "__main__":
    main()
