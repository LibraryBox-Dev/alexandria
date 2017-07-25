Uploads
*******

Modify the options that affect uploading.

.. note:: these settings affect only uploads made by non-authenticated users. There is
          no restriction on the uploads from authenticated users.

* Allow public uploads: Enabling this shows the upload button on all file views and allows users to upload files.
* Restrict uploadable filetypes: Enabling this whitelists the allowed extensions on files that may be uploaded
* Allowed filetypes for upload: These extensions are allowed to be uploaded when the *restrict uploadable filetypes* option is enabled.

.. warning:: these restrictions do not take into consideration the type of a file. For example, it will not keep someone from changing
             the extension of a file from `.exe` to `.jpg`. It also does not mean that a file could not be interpreted in multiple ways,
             for example a PDF which is also a valid game ROM.

Uploads are static and no content is allowed to execute code within the Alexandria context. This is a precaution against certain forms of attack.
 
Allowing uploads is a trait of the original PirateBox, which allowed users to upload any content they wished without hesitation.