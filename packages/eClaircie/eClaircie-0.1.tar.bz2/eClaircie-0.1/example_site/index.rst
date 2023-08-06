.. lang:: fr

Exemple de site
%%%%%%%%%%%%%%%

.. container:: float-right

   .. gallery:: eclaircie_logo.svg

Ceci est un exemple de site avec éClaircie.

éClaircie supporte les types de document suivants :

=======================  ============================================
**page statique**        fichier Restructured Text (\*.rst)

**catégorie**            sous-répertoire avec un fichier Restructured Text (\*/index.rst)

**post de blog**         fichier Restructured Text dont le nom commence par la date (ex 2014_05_30_titre.rst)

**fichier d'inclusion**  fichier Restructured Text (\*.inc), non affiché dans le site par défaut mais que vous pouvez inclure manuellement avec la directive ReST \.\. include\:\:

**script Python**        les scripts Python (\*.py) sont exécutés et peuvent générer du contenu
=======================  ============================================

Pour commencer un nouveau site avec éClaircie, il suffit de copier ce site exemple, et de le personnaliser.
Éditer le fichier conf.py pour cela. Ensuite, pour générer le site, utiliser la commande suivante :

::

   eclaircie /chemin/vers/conf.py

L'option "--force" permet de forcer la reconstruction de l'ensemble du site.


.. lang:: en

Example site
%%%%%%%%%%%%

.. container:: float-right

   .. gallery:: eclaircie_logo.svg

This is an example of site with éClaircie.

éClaircie supports the following types of documents:

=======================  ===================================================================================
**static page**          Restructured Text file (\*.rst)

**category**             subdirectory with a Restructured Text file (\*/index.rst)

**blog post**            Restructured Text file whose name starts with the date (ex 2014_05_30_titre.rst)

**include**              Restructured Text file (\*.inc), non-showed by default but you can include them manually with the \.\. include\:\: ReST directive

**Python script**        Python scripts (\*.py) are executed and can generated content
=======================  ===================================================================================


To start a new site with éClaircie, simply copy this example site, and customize it.
Edit the conf.py file for this. Then, to generate the site, use the following command:

::

   eclaircie /path/to/your/conf.py

The "--force" option allows to force the rebuiling of the whole site.
