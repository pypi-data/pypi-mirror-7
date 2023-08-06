.. automodule:: obiconvert

   *Examples:*
    
        .. code-block:: bash
    
                > obiconvert --ecopcrdb --fasta-output \
                  'my_ecopcr_database' > sequences.fasta

        Converts an ecoPCR database in a sequence file in *extended OBITools fasta* format.

   .. include:: ../optionsSet/taxonomyDB.txt
   
   .. include:: ../optionsSet/inputformat.txt
   
   .. include:: ../optionsSet/outputformat.txt

   .. include:: ../optionsSet/defaultoptions.txt
               

   :py:mod:`obiconvert` added sequence attributes
   ----------------------------------------------

       - :doc:`forward_error <../attributes/forward_error>`
       - :doc:`reverse_error <../attributes/reverse_error>`
       - :doc:`forward_match <../attributes/forward_match>`
       - :doc:`reverse_match <../attributes/reverse_match>`
       - :doc:`forward_tm <../attributes/forward_tm>`
       - :doc:`reverse_tm <../attributes/reverse_tm>`
       - :doc:`strand <../attributes/strand>`
               