<?php

namespace App\Libraries;

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

/**
 * EmailNotification — Librería centralizada de correos del sistema
 * 
 * Todos los módulos deben usar esta librería para enviar emails.
 * Usa PHPMailer con configuración SMTP del .env
 * 
 * Uso:
 *   $emailLib = new \App\Libraries\EmailNotification();
 *   $emailLib->enviarBienvenida('user@udg.mx', 'Juan');
 */
class EmailNotification
{
    private PHPMailer $mailer;
    private array $config;

    public function __construct()
    {
        $this->config = [
            'host'     => getenv('email.SMTPHost')   ?: 'smtp.udg.mx',
            'user'     => getenv('email.SMTPUser')   ?: '',
            'pass'     => getenv('email.SMTPPass')   ?: '',
            'port'     => getenv('email.SMTPPort')   ?: 587,
            'from'     => getenv('email.fromEmail')  ?: 'noreply@udg.mx',
            'fromName' => getenv('email.fromName')   ?: 'UDG-Proyectos',
            'crypto'   => getenv('email.SMTPCrypto') ?: 'tls',
        ];

        $this->mailer = $this->configurarMailer();
    }

    // ----------------------------------------------------------------
    // EMAILS DEL SISTEMA — Agregar métodos según necesidad
    // ----------------------------------------------------------------

    /** Email de bienvenida al registrarse */
    public function enviarBienvenida(string $destinatario, string $nombre): bool
    {
        $asunto = '¡Bienvenido a UDG-Proyectos!';
        $cuerpo = $this->template('bienvenida', [
            'nombre'  => $nombre,
            'link'    => base_url('auth/login'),
        ]);
        return $this->enviar($destinatario, $asunto, $cuerpo);
    }

    /** Email de recuperación de contraseña */
    public function enviarRecuperacion(string $destinatario, string $token): bool
    {
        $asunto = 'Recuperación de contraseña — UDG-Proyectos';
        $link   = base_url('auth/restablecer/' . $token);
        $cuerpo = $this->template('recuperacion', compact('link'));
        return $this->enviar($destinatario, $asunto, $cuerpo);
    }

    /** Notificación de proyecto enviado */
    public function notificarEnvioProyecto(string $destinatario, string $titulo, string $folio): bool
    {
        $asunto = "Proyecto recibido: {$folio}";
        $cuerpo = $this->template('proyecto_enviado', compact('titulo', 'folio'));
        return $this->enviar($destinatario, $asunto, $cuerpo);
    }

    /** Notificación de dictamen emitido */
    public function notificarDictamen(string $destinatario, string $titulo, string $dictamen, string $comentarios = ''): bool
    {
        $asunto = "Dictamen emitido para tu proyecto — UDG-Proyectos";
        $cuerpo = $this->template('dictamen', compact('titulo', 'dictamen', 'comentarios'));
        return $this->enviar($destinatario, $asunto, $cuerpo);
    }

    /** Notificación de asignación a evaluador */
    public function notificarAsignacion(string $destinatario, string $nombreEvaluador, string $titulo): bool
    {
        $asunto = "Proyecto asignado para revisión — UDG-Proyectos";
        $cuerpo = $this->template('asignacion', ['evaluador' => $nombreEvaluador, 'titulo' => $titulo]);
        return $this->enviar($destinatario, $asunto, $cuerpo);
    }

    // ----------------------------------------------------------------
    // MÉTODOS INTERNOS
    // ----------------------------------------------------------------

    /** Enviar email genérico */
    public function enviar(string $destinatario, string $asunto, string $cuerpo): bool
    {
        try {
            $this->mailer->clearAddresses();
            $this->mailer->addAddress($destinatario);
            $this->mailer->Subject = $asunto;
            $this->mailer->Body    = $cuerpo;
            $this->mailer->AltBody = strip_tags($cuerpo);
            return $this->mailer->send();
        } catch (Exception $e) {
            log_message('error', 'EmailNotification: ' . $e->getMessage());
            return false;
        }
    }

    /** Configurar PHPMailer con SMTP */
    private function configurarMailer(): PHPMailer
    {
        $mail = new PHPMailer(true);
        $mail->isSMTP();
        $mail->Host       = $this->config['host'];
        $mail->SMTPAuth   = true;
        $mail->Username   = $this->config['user'];
        $mail->Password   = $this->config['pass'];
        $mail->SMTPSecure = $this->config['crypto'];
        $mail->Port       = (int) $this->config['port'];
        $mail->CharSet    = 'UTF-8';
        $mail->isHTML(true);
        $mail->setFrom($this->config['from'], $this->config['fromName']);
        return $mail;
    }

    /**
     * Cargar plantilla HTML de email.
     * Las plantillas están en app/Views/emails/
     */
    private function template(string $nombre, array $datos = []): string
    {
        extract($datos);
        $path = APPPATH . "Views/emails/{$nombre}.php";
        if (! file_exists($path)) {
            return implode('<br>', array_map(
                fn($k, $v) => "<strong>{$k}:</strong> {$v}",
                array_keys($datos), $datos
            ));
        }
        ob_start();
        include $path;
        return ob_get_clean();
    }
}
