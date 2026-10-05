import 'package:flutter/material.dart';

import '../../core/localization/app_strings.dart';
import '../../shared/widgets/navimed_brand.dart';
import '../../shared/widgets/section_card.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key, required this.onSelectTab, required this.strings});

  final ValueChanged<int> onSelectTab;
  final AppStrings strings;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        const NaviMedBrand(),
        const SizedBox(height: 18),
        Text(strings.coordination, style: Theme.of(context).textTheme.bodyLarge),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(borderRadius: BorderRadius.circular(18), color: Theme.of(context).colorScheme.secondaryContainer),
          child: Row(children: [const Icon(Icons.verified_user_outlined), const SizedBox(width: 10), Expanded(child: Text(strings.authoritativeServiceNotice))]),
        ),
        const SizedBox(height: 20),
        SectionCard(icon: Icons.medical_services_outlined, title: strings.findProvider, onTap: () => onSelectTab(1)),
        const SizedBox(height: 12),
        SectionCard(icon: Icons.event_available_outlined, title: strings.myAppointments, onTap: () => onSelectTab(2)),
        const SizedBox(height: 12),
        SectionCard(icon: Icons.local_pharmacy_outlined, title: strings.onDuty, onTap: () => onSelectTab(3)),
        const SizedBox(height: 24),
        Text(strings.safeInformation, style: Theme.of(context).textTheme.bodySmall),
      ],
    );
  }
}
