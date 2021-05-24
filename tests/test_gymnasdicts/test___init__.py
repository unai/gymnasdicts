from gymnasdicts import Query


def test_chain():
    payload = {
        "patients": [
            {"id": 1, "name": "Bob", "dob": "1982-02-05"},
            {"id": 2, "name": "Sue", "dob": "2020-02-05"},
            {"id": 3, "name": "Sam", "dob": "2020-03-06"},
            {"id": 4, "name": "Kim", "dob": "2020-03-06"},
        ],
        "prescription": [
            {"id": 1, "price": 3, "drug": "Paracetamol"},
            {"id": 2, "price": 12, "drug": "Lisinopril"},
            {"id": 3, "price": 8, "drug": "Metformin"},
        ],
        "encounters": [
            {"id": 1, "patient_id": 1, "prescription_id": 1, "doctor": "Patel"},
            {"id": 2, "patient_id": 3, "prescription_id": 2, "doctor": "Patel"},
            {"id": 3, "patient_id": 3, "prescription_id": 1, "doctor": "Francis"},
            {"id": 4, "patient_id": 4, "prescription_id": 3, "doctor": "Francis"},
        ],
    }

    q = Query(payload)
    s = q.select(
        encounter_patient_id="$.encounters[*].patient_id",
        encounter_prescription_id="$.encounters[*].prescription_id",
        doctor="$.encounters[*].doctor",
        prescription_id="$.prescription[*].id",
        patient_id="$.patients[*].id",
        patient_name="$.patients[*].name",
        dob="$.patients[*].dob",
        price="$.prescription[*].price",
    )
    w = s.where(
        lambda encounter_prescription_id, prescription_id: encounter_prescription_id
        == prescription_id,
        lambda encounter_patient_id, patient_id: encounter_patient_id == patient_id,
        lambda dob: dob > "2020-01-01",
    )
    i = w.into(
        lambda price, doctor, patient_name: {
            "doctor": doctor,
            "patients": [patient_name],
            "cost": price,
        }
    )
    a = i.aggregate("$.['cost', 'patients']")
    expected = [
        {"doctor": "Patel", "patients": ["Sam"], "cost": 12},
        {"doctor": "Francis", "patients": ["Sam", "Kim"], "cost": 11},
    ]
    assert list(a) == expected
