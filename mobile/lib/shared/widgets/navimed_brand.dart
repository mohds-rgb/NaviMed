import 'package:flutter/material.dart';

class NaviMedBrand extends StatelessWidget {
  const NaviMedBrand({super.key, this.compact = false, this.showTagline = true});

  final bool compact;
  final bool showTagline;

  @override
  Widget build(BuildContext context) {
    final titleStyle = compact
        ? Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800)
        : Theme.of(context).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.w800);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(compact ? 14 : 18),
              child: Image.asset(
                'assets/branding/navimed_icon.png',
                width: compact ? 48 : 72,
                height: compact ? 48 : 72,
                fit: BoxFit.cover,
              ),
            ),
            const SizedBox(width: 14),
            Text('NaviMed', style: titleStyle),
          ],
        ),
        if (showTagline) ...[
          const SizedBox(height: 6),
          Text(
            'نافيميد  •  Dental & Health Network',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
        ],
      ],
    );
  }
}
