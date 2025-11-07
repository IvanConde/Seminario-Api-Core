-- =========================================================
-- SEMANA ANTERIOR: 27/10/2025 – 02/11/2025
-- =========================================================
-- Conversaciones
INSERT INTO conversations (channel_id, external_id, participant_identifier, participant_name, is_active, created_at, updated_at)
SELECT id, 'conv_whatsapp_aaa_20251027', '+54911-AAA', NULL, TRUE, '2025-10-27 12:00:00', '2025-10-27 12:03:00'
FROM channels WHERE name = 'whatsapp' LIMIT 1;

INSERT INTO conversations (channel_id, external_id, participant_identifier, participant_name, is_active, created_at, updated_at)
SELECT id, 'conv_gmail_cliente1_20251027', 'cliente1@gmail.com', NULL, TRUE, '2025-10-27 15:00:00', '2025-10-27 15:00:00'
FROM channels WHERE name = 'gmail' LIMIT 1;

INSERT INTO conversations (channel_id, external_id, participant_identifier, participant_name, is_active, created_at, updated_at)
SELECT id, 'conv_instagram_ig_user_01_20251028', 'ig_user_01', NULL, TRUE, '2025-10-28 14:10:00', '2025-10-28 14:14:00'
FROM channels WHERE name = 'instagram' LIMIT 1;

INSERT INTO conversations (channel_id, external_id, participant_identifier, participant_name, is_active, created_at, updated_at)
SELECT id, 'conv_whatsapp_bbb_20251029', '+54911-BBB', NULL, TRUE, '2025-10-29 10:00:00', '2025-10-29 10:05:00'
FROM channels WHERE name = 'whatsapp' LIMIT 1;

INSERT INTO conversations (channel_id, external_id, participant_identifier, participant_name, is_active, created_at, updated_at)
SELECT id, 'conv_gmail_cliente2_20251031', 'cliente2@gmail.com', NULL, TRUE, '2025-10-31 13:30:00', '2025-10-31 13:36:00'
FROM channels WHERE name = 'gmail' LIMIT 1;

INSERT INTO conversations (channel_id, external_id, participant_identifier, participant_name, is_active, created_at, updated_at)
SELECT id, 'conv_instagram_ig_user_02_20251101', 'ig_user_02', NULL, TRUE, '2025-11-01 16:20:00', '2025-11-01 16:20:00'
FROM channels WHERE name = 'instagram' LIMIT 1;

INSERT INTO conversations (channel_id, external_id, participant_identifier, participant_name, is_active, created_at, updated_at)
SELECT id, 'conv_whatsapp_ccc_20251102', '+54911-CCC', NULL, TRUE, '2025-11-02 11:00:00', '2025-11-02 11:10:00'
FROM channels WHERE name = 'whatsapp' LIMIT 1;

-- Mensajes
-- 27/10 - +54911-AAA
INSERT INTO messages (conversation_id, external_message_id, content, message_type, direction, sender_identifier, sender_name, timestamp, is_read, created_at)
SELECT id, 'msg_a_20251027_1', 'Hola, ¿tienen stock?', 'text', 'incoming', '+54911-AAA', NULL, '2025-10-27 12:00:00', FALSE, '2025-10-27 12:00:00'
FROM conversations WHERE external_id = 'conv_whatsapp_aaa_20251027';
INSERT INTO messages (conversation_id, external_message_id, content, message_type, direction, sender_identifier, sender_name, timestamp, is_read, created_at)
SELECT id, 'msg_a_20251027_2', 'Sí, ¿qué talle buscás?', 'text', 'outgoing', '+54911-AAA', NULL, '2025-10-27 12:03:00', TRUE, '2025-10-27 12:03:00'
FROM conversations WHERE external_id = 'conv_whatsapp_aaa_20251027';

-- 27/10 - cliente1@gmail.com
INSERT INTO messages (conversation_id, external_message_id, content, message_type, direction, sender_identifier, sender_name, timestamp, is_read, created_at)
SELECT id, 'msg_a_20251027_3', 'Quiero info de envíos', 'text', 'incoming', 'cliente1@gmail.com', NULL, '2025-10-27 15:00:00', FALSE, '2025-10-27 15:00:00'
FROM conversations WHERE external_id = 'conv_gmail_cliente1_20251027';

-- 28/10 - ig_user_01
INSERT INTO messages (conversation_id, external_message_id, content, message_type, direction, sender_identifier, sender_name, timestamp, is_read, created_at)
SELECT id, 'msg_a_20251028_1', 'Precio del combo?', 'text', 'incoming', 'ig_user_01', NULL, '2025-10-28 14:10:00', FALSE, '2025-10-28 14:10:00'
FROM conversations WHERE external_id = 'conv_instagram_ig_user_01_20251028';
INSERT INTO messages (conversation_id, external_message_id, content, message_type, direction, sender_identifier, sender_name, timestamp, is_read, created_at)
SELECT id, 'msg_a_20251028_2', 'Sale $25.000. ¿Te sirve?', 'text', 'outgoing', 'ig_user_01', NULL, '2025-10-28 14:14:00', TRUE, '2025-10-28 14:14:00'
FROM conversations WHERE external_id = 'conv_instagram_ig_user_01_20251028';

-- 29/10 - +54911-BBB
INSERT INTO messages (conversation_id, external_message_id, content, message_type, direction, sender_identifier, sender_name, timestamp, is_read, created_at)
SELECT id, 'msg_a_20251029_1', '¿Horario de atención?', 'text', 'incoming', '+54911-BBB', NULL, '2025-10-29 10:00:00', FALSE, '2025-10-29 10:00:00'
FROM conversations WHERE external_id = 'conv_whatsapp_bbb_20251029';
INSERT INTO messages (conversation_id, external_message_id, content, message_type, direction, sender_identifier, sender_name, timestamp, is_read, created_at)
SELECT id, 'msg_a_20251029_2', 'De 10 a 19 hs.', 'text', 'outgoing', '+54911-BBB', NULL, '2025-10-29 10:02:00', TRUE, '2025-10-29 10:02:00'
FROM conversations WHERE external_id = 'conv_whatsapp_bbb_20251029';
INSERT INTO messages (conversation_id, external_message_id, content, message_type, direction, sender_identifier, sender_name, timestamp, is_read, created_at)
SELECT id, 'msg_a_20251029_3', 'Gracias!', 'text', 'incoming', '+54911-BBB', NULL, '2025-10-29 10:05:00', TRUE, '2025-10-29 10:05:00'
FROM conversations WHERE external_id = 'conv_whatsapp_bbb_20251029';

-- 31/10 - cliente2@gmail.com
INSERT INTO messages (conversation_id, external_message_id, content, message_type, direction, sender_identifier, sender_name, timestamp, is_read, created_at)
SELECT id, 'msg_a_20251031_1', '¿Hacen factura A?', 'text', 'incoming', 'cliente2@gmail.com', NULL, '2025-10-31 13:30:00', FALSE, '2025-10-31 13:30:00'
FROM conversations WHERE external_id = 'conv_gmail_cliente2_20251031';
INSERT INTO messages (conversation_id, external_message_id, content, message_type, direction, sender_identifier, sender_name, timestamp, is_read, created_at)
SELECT id, 'msg_a_20251031_2', 'Sí, te pedimos CUIT y domicilio', 'text', 'outgoing', 'cliente2@gmail.com', NULL, '2025-10-31 13:36:00', TRUE, '2025-10-31 13:36:00'
FROM conversations WHERE external_id = 'conv_gmail_cliente2_20251031';

-- 01/11 - ig_user_02
INSERT INTO messages (conversation_id, external_message_id, content, message_type, direction, sender_identifier, sender_name, timestamp, is_read, created_at)
SELECT id, 'msg_a_20251101_1', '¿Dónde están ubicados?', 'text', 'incoming', 'ig_user_02', NULL, '2025-11-01 16:20:00', FALSE, '2025-11-01 16:20:00'
FROM conversations WHERE external_id = 'conv_instagram_ig_user_02_20251101';

-- 02/11 - +54911-CCC
INSERT INTO messages (conversation_id, external_message_id, content, message_type, direction, sender_identifier, sender_name, timestamp, is_read, created_at)
SELECT id, 'msg_a_20251102_1', 'Consulta por envío a CABA', 'text', 'incoming', '+54911-CCC', NULL, '2025-11-02 11:00:00', FALSE, '2025-11-02 11:00:00'
FROM conversations WHERE external_id = 'conv_whatsapp_ccc_20251102';
INSERT INTO messages (conversation_id, external_message_id, content, message_type, direction, sender_identifier, sender_name, timestamp, is_read, created_at)
SELECT id, 'msg_a_20251102_2', 'En CABA llega en 24/48 hs.', 'text', 'outgoing', '+54911-CCC', NULL, '2025-11-02 11:06:00', TRUE, '2025-11-02 11:06:00'
FROM conversations WHERE external_id = 'conv_whatsapp_ccc_20251102';
INSERT INTO messages (conversation_id, external_message_id, content, message_type, direction, sender_identifier, sender_name, timestamp, is_read, created_at)
SELECT id, 'msg_a_20251102_3', 'Dale, gracias', 'text', 'incoming', '+54911-CCC', NULL, '2025-11-02 11:10:00', TRUE, '2025-11-02 11:10:00'
FROM conversations WHERE external_id = 'conv_whatsapp_ccc_20251102';




-- =========================================================
-- SEMANA ACTUAL: 03/11/2025 – 09/11/2025
-- =========================================================
-- Conversaciones
INSERT INTO conversations (channel_id, external_id, participant_identifier, participant_name, is_active, created_at, updated_at)
SELECT id, 'conv_gmail_cliente3_20251103', 'cliente3@gmail.com', NULL, TRUE, '2025-11-03 12:00:00', '2025-11-03 12:04:00'
FROM channels WHERE name = 'gmail' LIMIT 1;

INSERT INTO conversations (channel_id, external_id, participant_identifier, participant_name, is_active, created_at, updated_at)
SELECT id, 'conv_instagram_ig_user_03_20251105', 'ig_user_03', NULL, TRUE, '2025-11-05 18:30:00', '2025-11-05 18:33:00'
FROM channels WHERE name = 'instagram' LIMIT 1;

INSERT INTO conversations (channel_id, external_id, participant_identifier, participant_name, is_active, created_at, updated_at)
SELECT id, 'conv_whatsapp_aaa_20251106', '+54911-AAA', NULL, TRUE, '2025-11-06 14:00:00', '2025-11-06 14:06:00'
FROM channels WHERE name = 'whatsapp' LIMIT 1;

INSERT INTO conversations (channel_id, external_id, participant_identifier, participant_name, is_active, created_at, updated_at)
SELECT id, 'conv_whatsapp_unknown_20251107', '+54911...', NULL, TRUE, '2025-11-07 00:00:00', '2025-11-07 00:03:00'
FROM channels WHERE name = 'whatsapp' LIMIT 1;

-- Mensajes
-- 03/11 - cliente3@gmail.com
INSERT INTO messages (conversation_id, external_message_id, content, message_type, direction, sender_identifier, sender_name, timestamp, is_read, created_at)
SELECT id, 'msg_b_20251103_1', '¿Hay pick-up en local?', 'text', 'incoming', 'cliente3@gmail.com', NULL, '2025-11-03 12:00:00', FALSE, '2025-11-03 12:00:00'
FROM conversations WHERE external_id = 'conv_gmail_cliente3_20251103';
INSERT INTO messages (conversation_id, external_message_id, content, message_type, direction, sender_identifier, sender_name, timestamp, is_read, created_at)
SELECT id, 'msg_b_20251103_2', 'Sí, de 10 a 19 hs', 'text', 'outgoing', 'cliente3@gmail.com', NULL, '2025-11-03 12:04:00', TRUE, '2025-11-03 12:04:00'
FROM conversations WHERE external_id = 'conv_gmail_cliente3_20251103';

-- 05/11 - ig_user_03
INSERT INTO messages (conversation_id, external_message_id, content, message_type, direction, sender_identifier, sender_name, timestamp, is_read, created_at)
SELECT id, 'msg_b_20251105_1', '¿Medios de pago?', 'text', 'incoming', 'ig_user_03', NULL, '2025-11-05 18:30:00', FALSE, '2025-11-05 18:30:00'
FROM conversations WHERE external_id = 'conv_instagram_ig_user_03_20251105';
INSERT INTO messages (conversation_id, external_message_id, content, message_type, direction, sender_identifier, sender_name, timestamp, is_read, created_at)
SELECT id, 'msg_b_20251105_2', 'Tarjeta, débito y transferencia', 'text', 'outgoing', 'ig_user_03', NULL, '2025-11-05 18:33:00', TRUE, '2025-11-05 18:33:00'
FROM conversations WHERE external_id = 'conv_instagram_ig_user_03_20251105';

-- 06/11 - +54911-AAA
INSERT INTO messages (conversation_id, external_message_id, content, message_type, direction, sender_identifier, sender_name, timestamp, is_read, created_at)
SELECT id, 'msg_b_20251106_1', 'Vuelvo por el tema del talle', 'text', 'incoming', '+54911-AAA', NULL, '2025-11-06 14:00:00', FALSE, '2025-11-06 14:00:00'
FROM conversations WHERE external_id = 'conv_whatsapp_aaa_20251106';
INSERT INTO messages (conversation_id, external_message_id, content, message_type, direction, sender_identifier, sender_name, timestamp, is_read, created_at)
SELECT id, 'msg_b_20251106_2', 'Te guardo M y L', 'text', 'outgoing', '+54911-AAA', NULL, '2025-11-06 14:06:00', TRUE, '2025-11-06 14:06:00'
FROM conversations WHERE external_id = 'conv_whatsapp_aaa_20251106';

-- 07/11 - +54911...
INSERT INTO messages (conversation_id, external_message_id, content, message_type, direction, sender_identifier, sender_name, timestamp, is_read, created_at)
SELECT id, 'msg_b_20251107_1', 'Hola', 'text', 'incoming', '+54911...', NULL, '2025-11-07 00:00:00', FALSE, '2025-11-07 00:00:00'
FROM conversations WHERE external_id = 'conv_whatsapp_unknown_20251107';
INSERT INTO messages (conversation_id, external_message_id, content, message_type, direction, sender_identifier, sender_name, timestamp, is_read, created_at)
SELECT id, 'msg_b_20251107_2', '¡Hola! ¿En qué puedo ayudarte?', 'text', 'outgoing', '+54911...', NULL, '2025-11-07 00:03:00', TRUE, '2025-11-07 00:03:00'
FROM conversations WHERE external_id = 'conv_whatsapp_unknown_20251107';
