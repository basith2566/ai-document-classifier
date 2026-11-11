Sample documents for testing the app (upload them on the Upload page):

resume_meera_nair.docx            -> expected: Resume
invoice_greenfield_supplies.pdf   -> expected: Invoice
research_paper_graph_networks.pdf -> expected: Research Paper
legal_nda_agreement.txt           -> expected: Legal Document
email_project_sync.txt            -> expected: Email
report_q3_operations.docx         -> expected: Report
recipe_lemon_cake.txt             -> expected: Other
meeting_minutes_mixed.txt         -> mixes report/legal/email language; usually "Needs Manual Review"
empty.txt                         -> rejected: file is empty
unsupported_data.csv              -> rejected: unsupported file type

These files are written by hand, separately from the training data, so they are a fair
(small) check that the model generalises beyond the synthetic templates. Results can vary
slightly if you retrain.
