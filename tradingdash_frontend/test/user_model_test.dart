import 'package:flutter_test/flutter_test.dart';
import 'package:tradingdash_frontend/models/user_model.dart';

void main() {
  test('UserProfile parses from and serializes to JSON', () {
    final json = {
      'phone_number': '+919876543210',
      'telegram_chat_id': '12345678',
      'whatsapp_alerts_enabled': true,
      'telegram_alerts_enabled': true,
      'default_exchange': 'MCX',
      'default_product': 'FUTURES',
      'favorite_symbols': ['GOLD', 'CRUDEOIL'],
    };

    final profile = UserProfile.fromJson(json);

    expect(profile.phoneNumber, '+919876543210');
    expect(profile.telegramChatId, '12345678');
    expect(profile.whatsappAlertsEnabled, true);
    expect(profile.telegramAlertsEnabled, true);
    expect(profile.defaultExchange, 'MCX');
    expect(profile.defaultProduct, 'FUTURES');
    expect(profile.favoriteSymbols, ['GOLD', 'CRUDEOIL']);

    final serialized = profile.toJson();
    expect(serialized['default_exchange'], 'MCX');
    expect(serialized['default_product'], 'FUTURES');
  });

  test('User parses from JSON with nested profile', () {
    final json = {
      'id': 1,
      'username': 'trader',
      'email': 'trader@example.com',
      'profile': {
        'phone_number': '',
        'telegram_chat_id': '998877',
        'whatsapp_alerts_enabled': false,
        'telegram_alerts_enabled': true,
        'default_exchange': 'NSE',
        'default_product': 'OPTIONS',
        'favorite_symbols': ['NIFTY'],
      },
    };

    final user = User.fromJson(json);

    expect(user.id, 1);
    expect(user.username, 'trader');
    expect(user.email, 'trader@example.com');
    expect(user.profile?.telegramChatId, '998877');
    expect(user.profile?.telegramAlertsEnabled, true);
  });
}
