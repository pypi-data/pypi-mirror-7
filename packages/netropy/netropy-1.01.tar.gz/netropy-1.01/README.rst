
Netropy
~~~~~~~

Netropy is a python interface to the `NIST Randomness Beacon`_.

API Quick Reference
~~~~~~~~~~~~~~~~~~~

.. code:: python


    # Get the current/latest record
    rec = beacon.current()

    # Retrieve the previous record for a given record
    rec_prev = beacon.previous(rec)

    # Retrieve the next record for a given record
    rec_next = beacon.next(rec)

    # Retrieve the last record in the chain
    rec_last = beacon.last()

    # Retrieve the first record in the chain
    rec_first = beacon.start_chain(rec)

    # Verify a record
    is_valid = record.verify_record(rec)

    # Verify two sequential records
    is_valid = record.verify_pair(rec1, rec2)

Examples
~~~~~~~~

A record is a dictionary representation of the xml record returned from
the beacon:

.. code:: python

    rec = beacon.current()
    pprint(rec)
    {'frequency': 60,
     'outputValue': u'742B8591BF3C291C129E4C84AD01DF17EFAE5EC18ECE5299C33F23BE9F88ED77A277CA7F161237EDB69D06D683A6501D314B7DF79307400AECC4298D46588DF8',
     'previousOutputValue': u'D52003A06C14F6CC7386B48F5CEBFE6BA583E2E6040E0698C26704AAFD6A7FC8F89D11B838E80255DB0FD9BB5DD48DC76A6C05A097B0D5E7537D65C7431E7A31',
     'seedValue': u'016BDBDA1F9D5A20D2350755B9A27F81B4B295007F998856C2DC30D2431E9082E6CD1DE77C70FD55B71DBF8807830E69F946635CE70781C535D6DE14E62E550B',
     'signatureValue': u'D309753214F976FB76E4325408FA5CA2EE1C514ABA7362C1A5CE1DB71078569DBF195F11F04CDAAB39B77318019A64BB5445F20D90EE8789F02E94BE7013F8D7DC70D5BBA8A310C469AA2E77175CAA4746C8385B7713B53BDD663A8940E8D55A514482EE2DD33883088F4B609351B2DBC4716FE4D047EA1BFC03D875A16B5B22ABF8AEE8BA341CABDB584E2A822196548CDA80D59DC6963B093BFBA316166E8331E66D984661957CBB68CCB8443362C75ACABB6B7407B41942CF9AB9CB17598E940298D4A7E7E5D6EF1945C77DF705496BEFDF13E3DC2C640462413094A0D6701CC9E3CAE6BA6A97EC9F67E07C49CFB64ECE9484B6F6DEA6AB531EF11F58201D',
     'statusCode': u'0',
     'timeStamp': 1396753680,
     'version': u'Version 1.0'}

Get the current record and print the random seed value:

.. code:: python

    import beacon

    rec_current = beacon.current()
    random_value = rec_current['seedValue']
    print(random_value)
    E1DB9B9919DF258E21E3A04D2D52E9F320097710588F25472E87608BEA0C72D1295B1D5EA5F199AD4E87A227BB5A4939073EBFCD512137AAD371C31299896341

Get the previous record:

.. code:: python

    import beacon

    rec_current = beacon.current()
    rec_previous = beacon.previous(rec_current)
    random_value = rec_previous['seedValue']
    print(random_value)
    299785EF23C8984459B6126222B6244E7AF0536C9EC5FF9A2D8105B0B7FB462CA0D691BCB99227D2E1337486AABF8169DE76F3D83FA2533AC9681174F926D9E3

Misc
~~~~

Expects python 2.6 / 2.7

.. _NIST Randomness Beacon: http://www.nist.gov/itl/csd/ct/nist_beacon.cfm


