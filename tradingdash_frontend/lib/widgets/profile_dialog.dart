import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/theme/app_theme.dart';
import '../models/user_model.dart';
import '../providers/auth_provider.dart';

class ProfileDialog extends ConsumerStatefulWidget {
  const ProfileDialog({super.key});

  @override
  ConsumerState<ProfileDialog> createState() => _ProfileDialogState();
}

class _ProfileDialogState extends ConsumerState<ProfileDialog> {
  late TextEditingController _phoneController;
  late TextEditingController _telegramController;
  late bool _whatsappEnabled;
  late bool _telegramEnabled;
  late String _defaultExchange;
  late String _defaultProduct;

  @override
  void initState() {
    super.initState();
    final profile = ref.read(authProvider).user?.profile;
    _phoneController = TextEditingController(text: profile?.phoneNumber ?? '');
    _telegramController =
        TextEditingController(text: profile?.telegramChatId ?? '');
    _whatsappEnabled = profile?.whatsappAlertsEnabled ?? false;
    _telegramEnabled = profile?.telegramAlertsEnabled ?? false;
    _defaultExchange = profile?.defaultExchange ?? 'NSE';
    _defaultProduct = profile?.defaultProduct ?? 'OPTIONS';
  }

  @override
  void dispose() {
    _phoneController.dispose();
    _telegramController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final user = authState.user;

    if (user == null) {
      return const SizedBox.shrink();
    }

    return Dialog(
      backgroundColor: AppTheme.surface,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: const BorderSide(color: AppTheme.border),
      ),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 480),
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        CircleAvatar(
                          backgroundColor:
                              const Color(0xFF3B82F6).withValues(alpha: 0.2),
                          child: Text(
                            user.username.isNotEmpty
                                ? user.username[0].toUpperCase()
                                : 'T',
                            style: const TextStyle(
                              color: Color(0xFF3B82F6),
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              user.username,
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 16,
                                color: Colors.white,
                              ),
                            ),
                            Text(
                              user.email.isNotEmpty
                                  ? user.email
                                  : 'Active Trader',
                              style: const TextStyle(
                                color: Colors.white54,
                                fontSize: 12,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                    IconButton(
                      icon: const Icon(Icons.close, color: Colors.white70),
                      onPressed: () => Navigator.of(context).pop(),
                    ),
                  ],
                ),
                const Divider(height: 32, color: AppTheme.border),
                const Text(
                  'Notification Channels',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _telegramController,
                  decoration: InputDecoration(
                    labelText: 'Telegram Chat ID',
                    prefixIcon: const Icon(Icons.send),
                    filled: true,
                    fillColor: AppTheme.background,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                ),
                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  title: const Text('Telegram Alerts Enabled'),
                  subtitle: const Text('Receive instant market signals'),
                  value: _telegramEnabled,
                  activeThumbColor: const Color(0xFF3B82F6),
                  onChanged: (val) => setState(() => _telegramEnabled = val),
                ),
                const SizedBox(height: 8),
                TextField(
                  controller: _phoneController,
                  decoration: InputDecoration(
                    labelText: 'WhatsApp Phone (+91...)',
                    prefixIcon: const Icon(Icons.phone),
                    filled: true,
                    fillColor: AppTheme.background,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                ),
                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  title: const Text('WhatsApp Alerts Enabled'),
                  subtitle: const Text('Receive critical breakout notices'),
                  value: _whatsappEnabled,
                  activeThumbColor: AppTheme.bullish,
                  onChanged: (val) => setState(() => _whatsappEnabled = val),
                ),
                const Divider(height: 24, color: AppTheme.border),
                const Text(
                  'Trading Preferences',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: DropdownButtonFormField<String>(
                        initialValue: _defaultExchange,
                        decoration: InputDecoration(
                          labelText: 'Default Exchange',
                          filled: true,
                          fillColor: AppTheme.background,
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(10),
                          ),
                        ),
                        dropdownColor: AppTheme.surface,
                        items: const [
                          DropdownMenuItem(value: 'NSE', child: Text('NSE')),
                          DropdownMenuItem(value: 'MCX', child: Text('MCX')),
                        ],
                        onChanged: (val) {
                          if (val != null) setState(() => _defaultExchange = val);
                        },
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: DropdownButtonFormField<String>(
                        initialValue: _defaultProduct,
                        decoration: InputDecoration(
                          labelText: 'Default Product',
                          filled: true,
                          fillColor: AppTheme.background,
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(10),
                          ),
                        ),
                        dropdownColor: AppTheme.surface,
                        items: const [
                          DropdownMenuItem(
                            value: 'OPTIONS',
                            child: Text('Options'),
                          ),
                          DropdownMenuItem(
                            value: 'FUTURES',
                            child: Text('Futures'),
                          ),
                        ],
                        onChanged: (val) {
                          if (val != null) setState(() => _defaultProduct = val);
                        },
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 28),
                Row(
                  children: [
                    TextButton.icon(
                      onPressed: () async {
                        await ref.read(authProvider.notifier).logout();
                        if (!context.mounted) return;
                        Navigator.of(context).pop();
                      },
                      icon: const Icon(Icons.logout, color: AppTheme.bearish),
                      label: const Text(
                        'Log Out',
                        style: TextStyle(color: AppTheme.bearish),
                      ),
                    ),
                    const Spacer(),
                    ElevatedButton(
                      onPressed: authState.isLoading ? null : _saveProfile,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF3B82F6),
                        padding: const EdgeInsets.symmetric(
                          horizontal: 20,
                          vertical: 12,
                        ),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10),
                        ),
                      ),
                      child: authState.isLoading
                          ? const SizedBox(
                              width: 18,
                              height: 18,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: Colors.white,
                              ),
                            )
                          : const Text(
                              'Save Changes',
                              style: TextStyle(fontWeight: FontWeight.bold),
                            ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _saveProfile() async {
    final updated = UserProfile(
      phoneNumber: _phoneController.text.trim(),
      telegramChatId: _telegramController.text.trim(),
      whatsappAlertsEnabled: _whatsappEnabled,
      telegramAlertsEnabled: _telegramEnabled,
      defaultExchange: _defaultExchange,
      defaultProduct: _defaultProduct,
    );

    final success =
        await ref.read(authProvider.notifier).updateProfile(updated);
    if (success && mounted) {
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Trader profile updated successfully!'),
          backgroundColor: AppTheme.bullish,
        ),
      );
      Navigator.of(context).pop();
    }
  }
}
