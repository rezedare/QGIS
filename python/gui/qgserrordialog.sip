/************************************************************************
 * This file has been generated automatically from                      *
 *                                                                      *
 * src/gui/qgserrordialog.h                                             *
 *                                                                      *
 * Do not edit manually ! Edit header and run scripts/sipify.pl again   *
 ************************************************************************/




class QgsErrorDialog: QDialog
{

%TypeHeaderCode
#include "qgserrordialog.h"
%End
  public:

    QgsErrorDialog( const QgsError &error, const QString &title, QWidget *parent /TransferThis/ = 0, Qt::WindowFlags fl = QgisGui::ModalDialogFlags );
%Docstring
 QgsErrorDialog constructor for QgsErrorDialog
%End

    static void show( const QgsError &error, const QString &title, QWidget *parent = 0, Qt::WindowFlags fl = QgisGui::ModalDialogFlags );
%Docstring
 Show dialog with error
 \param error error
 \param title title
 \param parent parent object
 \param fl widget flags
%End

  public slots:
    void on_mDetailPushButton_clicked();
    void on_mDetailCheckBox_stateChanged( int state );

};

/************************************************************************
 * This file has been generated automatically from                      *
 *                                                                      *
 * src/gui/qgserrordialog.h                                             *
 *                                                                      *
 * Do not edit manually ! Edit header and run scripts/sipify.pl again   *
 ************************************************************************/
