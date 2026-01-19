import 'package:flutter/material.dart';
import '../services/socket_service.dart';

class AddExpenseScreen extends StatefulWidget {
  const AddExpenseScreen({super.key});

  @override
  State<AddExpenseScreen> createState() => _AddExpenseScreenState();
}

class _AddExpenseScreenState extends State<AddExpenseScreen> {
  final amountController = TextEditingController();
  final noteController = TextEditingController();
  String category = "Food";

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Add Expense")),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              controller: amountController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: "Amount"),
            ),
            DropdownButton<String>(
              value: category,
              items: const [
                DropdownMenuItem(value: "Food", child: Text("Food")),
                DropdownMenuItem(value: "Travel", child: Text("Travel")),
                DropdownMenuItem(value: "Shopping", child: Text("Shopping")),
              ],
              onChanged: (v) => setState(() => category = v!),
            ),
            TextField(
              controller: noteController,
              decoration: const InputDecoration(labelText: "Note"),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () async {
                await SocketService().addExpense(
                  amount: double.parse(amountController.text),
                  category: category,
                  note: noteController.text,
                );
                Navigator.pop(context);
              },
              child: const Text("Save"),
            )
          ],
        ),
      ),
    );
  }
}
