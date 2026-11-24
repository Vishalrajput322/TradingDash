class UserProfile {
  final String? phoneNumber;
  final String? telegramChatId;
  final bool whatsappAlertsEnabled;
  final bool telegramAlertsEnabled;
  final String defaultExchange;
  final String defaultProduct;
  final List<String> favoriteSymbols;
  final String? updatedAt;

  const UserProfile({
    this.phoneNumber,
    this.telegramChatId,
    this.whatsappAlertsEnabled = false,
    this.telegramAlertsEnabled = false,
    this.defaultExchange = 'NSE',
    this.defaultProduct = 'OPTIONS',
    this.favoriteSymbols = const [],
    this.updatedAt,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      phoneNumber: json['phone_number'] as String?,
      telegramChatId: json['telegram_chat_id'] as String?,
      whatsappAlertsEnabled: json['whatsapp_alerts_enabled'] as bool? ?? false,
      telegramAlertsEnabled: json['telegram_alerts_enabled'] as bool? ?? false,
      defaultExchange: (json['default_exchange'] as String?) ?? 'NSE',
      defaultProduct: (json['default_product'] as String?) ?? 'OPTIONS',
      favoriteSymbols: (json['favorite_symbols'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          const [],
      updatedAt: json['updated_at'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'phone_number': phoneNumber ?? '',
      'telegram_chat_id': telegramChatId ?? '',
      'whatsapp_alerts_enabled': whatsappAlertsEnabled,
      'telegram_alerts_enabled': telegramAlertsEnabled,
      'default_exchange': defaultExchange,
      'default_product': defaultProduct,
      'favorite_symbols': favoriteSymbols,
    };
  }

  UserProfile copyWith({
    String? phoneNumber,
    String? telegramChatId,
    bool? whatsappAlertsEnabled,
    bool? telegramAlertsEnabled,
    String? defaultExchange,
    String? defaultProduct,
    List<String>? favoriteSymbols,
  }) {
    return UserProfile(
      phoneNumber: phoneNumber ?? this.phoneNumber,
      telegramChatId: telegramChatId ?? this.telegramChatId,
      whatsappAlertsEnabled:
          whatsappAlertsEnabled ?? this.whatsappAlertsEnabled,
      telegramAlertsEnabled:
          telegramAlertsEnabled ?? this.telegramAlertsEnabled,
      defaultExchange: defaultExchange ?? this.defaultExchange,
      defaultProduct: defaultProduct ?? this.defaultProduct,
      favoriteSymbols: favoriteSymbols ?? this.favoriteSymbols,
      updatedAt: updatedAt,
    );
  }
}

class User {
  final int id;
  final String username;
  final String email;
  final String? firstName;
  final String? lastName;
  final UserProfile? profile;

  const User({
    required this.id,
    required this.username,
    required this.email,
    this.firstName,
    this.lastName,
    this.profile,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as int,
      username: json['username'] as String,
      email: json['email'] as String? ?? '',
      firstName: json['first_name'] as String?,
      lastName: json['last_name'] as String?,
      profile: json['profile'] != null
          ? UserProfile.fromJson(json['profile'] as Map<String, dynamic>)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'email': email,
      'first_name': firstName,
      'last_name': lastName,
      if (profile != null) 'profile': profile!.toJson(),
    };
  }
}

class AuthResponse {
  final User user;
  final String access;
  final String refresh;

  const AuthResponse({
    required this.user,
    required this.access,
    required this.refresh,
  });

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      user: User.fromJson(json['user'] as Map<String, dynamic>),
      access: json['access'] as String,
      refresh: json['refresh'] as String,
    );
  }
}
