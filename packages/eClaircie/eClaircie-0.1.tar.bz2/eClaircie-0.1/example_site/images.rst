.. lang:: fr
Images
======

Les images peuvent être insérer avec la directive \.\. figure\:\: :

.. lang:: en

Images
======

You can insert an image with the \.\. figure\:\: directive:


.. lang:: all

.. code-block:: rest

   .. figure:: /_images/zaurus.jpeg

.. figure:: /_images/zaurus.jpeg


.. lang:: fr

éClaircie dispose aussi de la directive \.\. gallery\:\: .
Cette directive prend pour paramètre une liste de nom de fichiers ou de sous-répertoires, localisés dans /_images/.


.. lang:: en

éClaircie also has the \.\. gallery\:\: directive. It takes as parameter a list of filenames or
subdirectories, located in /_images/.


.. lang:: all

.. code-block:: rest

   .. gallery:: zaurus.jpeg zaurus_et_ordi.jpeg

.. gallery:: zaurus.jpeg zaurus_et_ordi.jpeg


.. lang:: fr

Enfin, la directive \.\. container\:\: avec la classe CSS "float-right" permet de positionner des
éléments sur la droite.

.. lang:: en

Finally, the \.\. container\:\: directive with the CSS class "float-right" can be used to position
elements on the right.

.. lang:: all

.. code-block:: rest

   .. container:: float-right

      .. gallery:: eclaircie_logo.svg

