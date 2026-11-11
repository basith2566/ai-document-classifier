"""
Builds dataset/training_data.csv (columns: text,label).

This is a DATA tool, not part of the web application. It assembles documents
from randomised phrase pools so the project ships with a working starter
dataset. The data is synthetic: the model trained on it is a demonstration, not
a production system. For real use, replace training_data.csv with real,
labelled documents (same two columns) and retrain.

Usage (from the backend/ folder):
    python dataset/generate_training_data.py
"""
import csv
import random
from pathlib import Path

random.seed(42)
SAMPLES_PER_CATEGORY = 150
OUT = Path(__file__).resolve().parent / "training_data.csv"

FIRST = ["Aarav", "Maria", "John", "Priya", "Liam", "Fatima", "Chen", "Sofia", "Omar", "Emma", "Ravi", "Hannah", "Diego", "Aisha", "Noah", "Meera", "Lucas", "Zara", "Ethan", "Nadia"]
LAST = ["Sharma", "Garcia", "Smith", "Patel", "Johnson", "Khan", "Wang", "Rossi", "Hassan", "Brown", "Kumar", "Miller", "Lopez", "Ali", "Davis", "Nair", "Silva", "Ahmed", "Wilson", "Iyer"]
COMPANIES = ["Northwind Systems", "Bluepeak Technologies", "Orchid Analytics", "Vertex Logistics", "Sunrise Retail Group", "Helios Software", "Cedar Financial", "Atlas Manufacturing", "Pinnacle Health", "Lumen Media"]
CITIES = ["Chennai", "Austin", "London", "Toronto", "Berlin", "Singapore", "Dubai", "Sydney", "Chicago", "Bangalore"]
TOPICS = ["machine learning", "data engineering", "web development", "cloud infrastructure", "cyber security", "product management", "customer support", "financial analysis"]


def pick(seq):
    return random.choice(seq)


def name():
    return f"{pick(FIRST)} {pick(LAST)}"


def email(n=None):
    n = n or name()
    return n.lower().replace(" ", ".") + "@" + pick(["gmail.com", "outlook.com", "company.com", "mail.org", "example.com"])


def phone():
    return f"+{random.randint(1, 91)} {random.randint(70000, 99999)} {random.randint(10000, 99999)}"


def date():
    return f"{random.randint(1, 28):02d}/{random.randint(1, 12):02d}/{random.randint(2021, 2026)}"


# ----------------------------------------------------------------- Resume
def resume():
    n = name()
    skills = random.sample(["Python", "SQL", "Java", "React", "Docker", "AWS", "Git", "Excel", "TensorFlow", "Tableau", "Linux", "Communication", "Leadership", "Teamwork", "Project management", "REST APIs", "Pandas", "Figma"], k=random.randint(6, 10))
    parts = [n.upper(), f"{email(n)} | {phone()} | {pick(CITIES)} | linkedin.com/in/{n.lower().replace(' ', '')}"]
    parts.append(pick(["Professional Summary", "Career Objective", "Summary", "Profile"]))
    parts.append(f"{pick(['Motivated', 'Detail-oriented', 'Results-driven', 'Enthusiastic'])} {pick(['software engineer', 'data analyst', 'graduate', 'developer', 'business analyst'])} with {random.randint(1, 9)} years of experience in {pick(TOPICS)}. Seeking a challenging role to apply my skills and grow professionally.")
    parts.append("Skills")
    parts.append(", ".join(skills))
    parts.append(pick(["Work Experience", "Professional Experience", "Experience"]))
    for _ in range(random.randint(1, 3)):
        y = random.randint(2015, 2023)
        parts.append(f"{pick(['Software Engineer', 'Data Analyst', 'Intern', 'Team Lead', 'Consultant', 'Developer'])}, {pick(COMPANIES)} ({y} - {pick(['Present', str(y + random.randint(1, 3))])})")
        parts.append(f"- {pick(['Developed', 'Designed', 'Implemented', 'Managed', 'Improved'])} {pick(['dashboards', 'APIs', 'data pipelines', 'internal tools', 'customer workflows'])} that {pick(['reduced processing time by 30%', 'increased team productivity', 'served 10,000 users', 'cut costs by 15%'])}.")
        parts.append(f"- Collaborated with cross-functional teams and mentored {random.randint(2, 6)} junior members.")
    parts.append("Education")
    parts.append(f"{pick(['B.Tech', 'B.Sc', 'M.Sc', 'MBA', 'Bachelor of Engineering'])} in {pick(['Computer Science', 'Artificial Intelligence and Data Science', 'Information Technology', 'Statistics'])}, {pick(['Crescent Institute', 'State University', 'Institute of Technology', 'City College'])}, CGPA {random.randint(70, 98) / 10}")
    if random.random() < 0.7:
        parts.append(pick(["Certifications", "Projects", "Achievements"]))
        parts.append(f"{pick(['AWS Certified Cloud Practitioner', 'Google Data Analytics Certificate', 'Hackathon winner', 'Built a sentiment analysis app'])}; {pick(['Deans list', 'Open-source contributor', 'Volunteer coordinator'])}")
    if random.random() < 0.4:
        parts.append("References available upon request.")
    return "\n".join(parts)


# ---------------------------------------------------------------- Invoice
def invoice():
    items = []
    subtotal = 0.0
    for _ in range(random.randint(2, 6)):
        qty = random.randint(1, 20)
        price = float(random.randint(5, 900))
        subtotal += qty * price
        items.append(f"{pick(['Consulting services', 'Web hosting plan', 'Office supplies', 'Software license', 'Maintenance contract', 'Design work', 'Shipping and handling', 'Hardware components'])}  Qty {qty}  Unit price {price:.2f}  Amount {qty * price:.2f}")
    tax_rate = pick([5, 8, 10, 12, 18, 20])
    tax = subtotal * tax_rate / 100
    parts = [
        pick(["INVOICE", "TAX INVOICE", "Invoice", "SALES INVOICE"]),
        f"Invoice No: INV-{random.randint(1000, 99999)}",
        f"Invoice Date: {date()}    Due Date: {date()}",
        f"From: {pick(COMPANIES)}, {pick(CITIES)}",
        f"Bill To: {name()}, {pick(COMPANIES)}",
        pick(["PO Number", "Order Ref", "Customer ID"]) + f": {random.randint(10000, 99999)}",
        "Description  Quantity  Rate  Amount",
        *items,
        f"Subtotal: {subtotal:.2f}",
        f"{pick(['Tax', 'VAT', 'GST', 'Sales Tax'])} ({tax_rate}%): {tax:.2f}",
        f"{pick(['Total Due', 'Amount Payable', 'Balance Due', 'Grand Total'])}: {subtotal + tax:.2f}",
        pick(["Payment terms: Net 30 days.", "Payment due within 15 days of invoice date.", "Please remit payment by the due date."]),
        pick(["Bank transfer to account ending " + str(random.randint(1000, 9999)) + ".", "Cheques payable to the company name above.", "Pay online using the link on your statement."]),
        pick(["Thank you for your business.", "Late payments are subject to a 1.5% monthly fee.", "Questions about this invoice? Contact accounts receivable."]),
    ]
    return "\n".join(parts)


# --------------------------------------------------------- Research paper
def research_paper():
    topic = pick(["transformer models", "federated learning", "graph neural networks", "anomaly detection", "reinforcement learning", "image segmentation", "text classification", "protein folding", "climate forecasting", "intrusion detection"])
    method = pick(["a novel attention mechanism", "a hybrid deep learning framework", "a self-supervised pretraining strategy", "an ensemble approach", "a lightweight convolutional architecture"])
    authors = ", ".join(name() for _ in range(random.randint(2, 4)))
    parts = [
        f"{pick(['Improving', 'Towards Robust', 'A Study of', 'Efficient', 'On the Limits of'])} {topic.title()} {pick(['with Limited Data', 'at Scale', 'Using Deep Learning', 'A Comparative Analysis'])}",
        authors,
        f"Department of Computer Science, {pick(['University of Technology', 'Institute of Science', 'National Research Laboratory'])}",
        "Abstract",
        f"In this paper we propose {method} for {topic}. Extensive experiments on {random.randint(2, 5)} benchmark datasets show that our method outperforms state-of-the-art baselines by {random.randint(2, 12)}.{random.randint(0, 9)}% in accuracy. We also provide an ablation study and discuss limitations.",
        f"Keywords: {topic}, {pick(['deep learning', 'optimization', 'neural networks', 'benchmark'])}, {pick(['generalization', 'robustness', 'scalability'])}",
        "1. Introduction",
        f"Recent advances in {topic} have attracted significant attention in the research community [1], [2]. However, existing approaches suffer from {pick(['high computational cost', 'poor generalization', 'sensitivity to noise', 'reliance on large labelled datasets'])}. The main contributions of this work are summarised as follows.",
        "2. Related Work",
        f"Prior studies by {pick(LAST)} et al. [3] and {pick(LAST)} and {pick(LAST)} [4] explored {topic}. Our work differs in that we hypothesize that {pick(['pretraining', 'regularization', 'data augmentation'])} plays a central role.",
        "3. Methodology",
        f"We formulate the problem as minimizing the loss function L over the training set. The model is optimized using Adam with learning rate {pick(['1e-3', '3e-4', '1e-4'])}. Figure {random.randint(1, 4)} illustrates the architecture.",
        "4. Experiments and Results",
        f"We evaluate on {pick(['CIFAR-10', 'ImageNet', 'GLUE', 'MNIST', 'UCI repository datasets'])}. Table {random.randint(1, 3)} reports precision, recall and F1-score. Results are statistically significant (p < 0.0{random.randint(1, 5)}).",
        "5. Conclusion",
        f"We presented {method} and demonstrated its effectiveness. Future work will investigate {pick(['larger datasets', 'theoretical guarantees', 'real-world deployment'])}.",
        "References",
        f"[1] {name()}, \"{pick(['Deep learning', 'Attention is useful', 'Scalable methods'])}\", Journal of Machine Learning Research, vol. {random.randint(10, 60)}, {random.randint(2015, 2025)}.",
        f"[2] {name()}, Proceedings of the International Conference on {pick(['Learning Representations', 'Machine Learning', 'Neural Information Processing'])}, {random.randint(2016, 2025)}. doi:10.{random.randint(1000, 9999)}/{random.randint(10000, 99999)}",
    ]
    return "\n".join(parts)


# --------------------------------------------------------- Legal document
def legal():
    a, b = pick(COMPANIES), pick(COMPANIES)
    kind = pick(["NON-DISCLOSURE AGREEMENT", "SERVICE AGREEMENT", "LEASE AGREEMENT", "EMPLOYMENT CONTRACT", "SOFTWARE LICENSE AGREEMENT", "SETTLEMENT AGREEMENT"])
    clauses = [
        "1. Definitions. In this Agreement, \"Confidential Information\" means all non-public information disclosed by either party, hereinafter referred to as the \"Disclosing Party\".",
        f"2. Term. This Agreement shall commence on the Effective Date and continue for a period of {random.randint(1, 5)} years unless terminated earlier in accordance with Section {random.randint(5, 12)}.",
        "3. Obligations. The Receiving Party shall not disclose, notwithstanding any other provision, any information to third parties without prior written consent.",
        "4. Indemnification. Each party shall indemnify and hold harmless the other party against all claims, damages, liabilities and expenses arising from any breach of this Agreement.",
        f"5. Termination. Either party may terminate this Agreement upon {random.randint(15, 90)} days written notice. Upon termination, all rights and obligations shall cease, save for those which by their nature survive.",
        f"6. Governing Law. This Agreement shall be governed by and construed in accordance with the laws of {pick(['the State of California', 'England and Wales', 'India', 'the State of New York'])}, and the courts of {pick(CITIES)} shall have exclusive jurisdiction.",
        "7. Limitation of Liability. In no event shall either party be liable for indirect, incidental or consequential damages.",
        "8. Entire Agreement. This Agreement constitutes the entire agreement between the parties and supersedes all prior negotiations, representations and understandings.",
        "9. Force Majeure. Neither party shall be liable for failure to perform due to causes beyond its reasonable control.",
    ]
    random.shuffle(clauses)
    parts = [
        kind,
        f"This Agreement is made and entered into on {date()} by and between {a}, having its registered office at {pick(CITIES)} (the \"Company\"), and {b} (the \"Counterparty\").",
        f"WHEREAS the Company desires to engage the Counterparty for {pick(['the provision of services', 'the licensing of software', 'the lease of premises', 'the exchange of confidential information'])}; and WHEREAS the parties wish to set out their respective rights and obligations;",
        "NOW, THEREFORE, in consideration of the mutual covenants herein, the parties agree as follows:",
        *clauses[: random.randint(5, 9)],
        "IN WITNESS WHEREOF, the parties hereto have executed this Agreement as of the date first written above.",
        f"Signed: ______________ {name()}   Witness: ______________ {name()}",
    ]
    return "\n".join(parts)


# ------------------------------------------------------------------ Email
def email_doc():
    s, r = name(), name()
    subject = pick(["Meeting tomorrow", "Project update", "Quick question", "Re: Proposal feedback", "Fwd: Schedule for next week", "Follow up on our call", "Documents attached", "Lunch on Friday?", "Re: Access request"])
    body = random.sample([
        f"I wanted to follow up on {pick(['our discussion yesterday', 'the proposal', 'the project timeline', 'the open tickets'])}.",
        f"Could you please send me the {pick(['updated spreadsheet', 'slides', 'signed form', 'latest draft'])} by {pick(['Monday', 'end of day', 'Thursday', 'tomorrow morning'])}?",
        f"Please find attached the {pick(['document', 'report', 'presentation', 'agenda'])} for your review.",
        "Let me know if that works for you.",
        f"I'm available {pick(['Tuesday', 'Wednesday', 'Friday'])} afternoon if you'd like to catch up.",
        "Thanks for getting back to me so quickly.",
        "Sorry for the delay in replying, I was out of office last week.",
        f"Can we move the meeting to {random.randint(1, 5)} PM?",
    ], k=random.randint(2, 5))
    parts = [
        f"From: {s} <{email(s)}>",
        f"To: {r} <{email(r)}>",
        *([f"Cc: {email()}"] if random.random() < 0.3 else []),
        f"Subject: {subject}",
        f"Date: {pick(['Mon', 'Tue', 'Wed', 'Thu', 'Fri'])}, {random.randint(1, 28)} {pick(['Jan', 'Mar', 'May', 'Aug', 'Oct'])} {random.randint(2022, 2026)} {random.randint(8, 18)}:{random.randint(10, 59)}",
        "",
        f"{pick(['Hi', 'Hello', 'Dear', 'Hey'])} {r.split()[0]},",
        "",
        *body,
        "",
        pick(["Best regards,", "Thanks,", "Kind regards,", "Cheers,", "Regards,", "Thank you,"]),
        s.split()[0],
        *([pick(["Sent from my iPhone", "Sent from my Android device", "Get Outlook for iOS"])] if random.random() < 0.4 else []),
    ]
    return "\n".join(parts)


# ----------------------------------------------------------------- Report
def report():
    dept = pick(["Sales", "Operations", "Marketing", "Finance", "Human Resources", "IT Infrastructure", "Customer Success"])
    parts = [
        f"{pick(['Quarterly', 'Annual', 'Monthly', 'Project Status', 'Performance'])} {pick(['Report', 'Review', 'Summary Report'])}: {dept} Department",
        f"Prepared by: {name()}    Date: {date()}    Distribution: Management Team",
        "Executive Summary",
        f"This report summarises the performance of the {dept} department during the reporting period. Overall results were {pick(['in line with targets', 'above expectations', 'below target in some areas'])}, with notable progress in {pick(['customer retention', 'cost control', 'delivery timelines', 'team hiring'])}.",
        "Key Findings",
        f"- Revenue {pick(['increased', 'decreased', 'remained stable'])} by {random.randint(1, 25)}% compared with the previous period.",
        f"- {pick(['Customer satisfaction', 'Employee engagement', 'System uptime', 'On-time delivery'])} reached {random.randint(70, 99)}%.",
        f"- {random.randint(2, 15)} milestones were completed; {random.randint(0, 4)} remain in progress.",
        "Analysis",
        f"The data indicates that {pick(['seasonal demand', 'new tooling', 'staffing changes', 'market conditions'])} had a significant impact on outcomes. Variance against budget was {random.randint(1, 9)}%.",
        "Risks and Issues",
        f"- {pick(['Supplier delays', 'Budget constraints', 'Resource shortages', 'Security vulnerabilities'])} may affect the next quarter.",
        "Recommendations",
        f"1. {pick(['Increase investment in', 'Review the process for', 'Allocate additional staff to', 'Introduce monitoring for'])} {pick(['onboarding', 'reporting', 'procurement', 'customer support'])}.",
        f"2. {pick(['Schedule a follow-up review', 'Update the project plan', 'Present findings to the steering committee'])} by {date()}.",
        "Next Steps and Conclusion",
        "The team will continue to track key performance indicators and provide a further status update next period.",
    ]
    return "\n".join(parts)


# ------------------------------------------------------------------ Other
def other():
    kind = random.choice(["recipe", "travel", "sports", "product", "story", "fitness", "review"])
    if kind == "recipe":
        return "\n".join([
            f"{pick(['Creamy', 'Spicy', 'Classic', 'Easy'])} {pick(['tomato pasta', 'chicken curry', 'vegetable soup', 'chocolate cake', 'banana pancakes'])}",
            f"Serves {random.randint(2, 8)}. Prep time {random.randint(10, 40)} minutes. Cook time {random.randint(15, 60)} minutes.",
            "Ingredients: " + ", ".join(random.sample(["2 cups flour", "3 ripe tomatoes", "1 tsp salt", "olive oil", "fresh basil", "2 cloves garlic", "1 onion, chopped", "250g butter", "half a cup of sugar", "a pinch of pepper"], k=6)),
            f"Method: Heat the oil in a large pan and {pick(['saute the onions', 'stir in the spices', 'whisk the eggs'])} until golden. Add the remaining ingredients, stir well and simmer for {random.randint(10, 30)} minutes. Serve hot and enjoy with your family.",
        ])
    if kind == "travel":
        return f"Last summer we spent {random.randint(3, 10)} days exploring {pick(CITIES)}. The streets were full of colour, the food was unforgettable and the locals were incredibly friendly. We hiked up to a viewpoint at sunrise, tried street food at the night market and took a boat ride along the coast. If you are planning a trip, book your hotel early and pack comfortable shoes. Highly recommended for anyone who loves adventure and photography."
    if kind == "sports":
        return f"{pick(['United', 'City', 'Rovers', 'Warriors', 'Strikers'])} secured a dramatic {random.randint(1, 4)}-{random.randint(0, 3)} victory on Saturday, with a stunning goal in the final minutes sending the crowd wild. The coach praised the players for their fighting spirit. The team now sits {pick(['second', 'third', 'top'])} in the league table ahead of next weekend's derby."
    if kind == "product":
        return f"Introducing the new {pick(['UltraBlend', 'SkyPods', 'TrailMax', 'HomeGlow'])} {pick(['blender', 'earbuds', 'backpack', 'smart lamp'])}. Lightweight, durable and stylish, it is designed for everyday life. Available in {random.randint(3, 6)} colours with free delivery and a {random.randint(1, 3)}-year warranty. Order today and get 20% off your first purchase. Limited stock available."
    if kind == "story":
        return f"The old lighthouse stood silent against the grey sky. {pick(['Maya', 'Arjun', 'Leo', 'Sana'])} pulled her coat tighter and walked toward the door, her heart pounding. Nobody had entered the tower for years, yet a faint light flickered in the highest window. She hesitated, whispered a quiet prayer and began to climb the winding stairs, one step at a time."
    if kind == "fitness":
        return f"Beginner workout guide: start with a {random.randint(5, 10)}-minute warm-up, then do {random.randint(2, 4)} sets of squats, push-ups and planks. Rest for 60 seconds between sets. Drink plenty of water, sleep well and increase intensity slowly each week. Consistency matters more than perfection, so find an activity you enjoy."
    return f"I watched this film last weekend and loved it. The acting was brilliant, the soundtrack was beautiful and the ending left me speechless. The plot drags a little in the middle, but overall it is a wonderful way to spend an evening. I would give it {random.randint(3, 5)} out of 5 stars and recommend it to friends."


GENERATORS = {
    "Resume": resume,
    "Invoice": invoice,
    "Research Paper": research_paper,
    "Legal Document": legal,
    "Email": email_doc,
    "Report": report,
    "Other": other,
}


def maybe_truncate(text):
    """Real documents are often partial; simulate that for ~25% of samples."""
    if random.random() < 0.25:
        words = text.split()
        keep = max(25, int(len(words) * random.uniform(0.5, 0.9)))
        return " ".join(words[:keep])
    return text


def main():
    rows, seen = [], set()
    for label, fn in GENERATORS.items():
        count, attempts = 0, 0
        while count < SAMPLES_PER_CATEGORY and attempts < SAMPLES_PER_CATEGORY * 20:
            attempts += 1
            text = maybe_truncate(fn())
            if text in seen:
                continue
            seen.add(text)
            rows.append((text, label))
            count += 1
    random.shuffle(rows)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "label"])
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
