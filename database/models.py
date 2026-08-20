from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database.db_config import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)  # admin, prof, parent

class AnneeScolaire(Base):
    __tablename__ = 'annees_scolaires'
    id = Column(Integer, primary_key=True, index=True)
    libelle = Column(String, unique=True)
    active = Column(Boolean, default=False)

class Classe(Base):
    __tablename__ = 'classes'
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, unique=True)
    cycle = Column(String)  # Primaire, Collège, Lycée, etc.
    tarif_scolarite = Column(Float, default=0.0)
    
    eleves = relationship("Eleve", back_populates="classe")

class Eleve(Base):
    __tablename__ = 'eleves'
    id = Column(Integer, primary_key=True, index=True)
    matricule = Column(String, unique=True, index=True)
    nom = Column(String)
    prenom = Column(String)
    sexe = Column(String)
    telephone = Column(String, nullable=True)
    montant_reduction = Column(Float, default=0.0)
    classe_id = Column(Integer, ForeignKey('classes.id'))
    photo = Column(String, nullable=True)
    
    classe = relationship("Classe", back_populates="eleves")

class Matiere(Base):
    __tablename__ = 'matieres'
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, unique=True)
    coefficient = Column(Integer, default=1)

class Programme(Base):
    __tablename__ = 'programmes'
    id = Column(Integer, primary_key=True, index=True)
    classe_id = Column(Integer, ForeignKey('classes.id'))
    matiere_id = Column(Integer, ForeignKey('matieres.id'))
    volume_horaire_prevu = Column(Float, default=30.0)
    semestre = Column(Integer, default=1)
    document_pdf = Column(String, nullable=True)  # <-- Ajout de la colonne manquante
    
    classe = relationship("Classe")
    matiere = relationship("Matiere")

class Enseignant(Base):
    __tablename__ = 'enseignants'
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String)
    prenom = Column(String)
    specialite = Column(String, nullable=True)
    telephone = Column(String, nullable=True)

class Personnel(Base):
    __tablename__ = 'personnels'
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String)
    prenom = Column(String)
    fonction = Column(String, nullable=True)
    telephone = Column(String, nullable=True)

class Depense(Base):
    __tablename__ = 'depenses'
    id = Column(Integer, primary_key=True, index=True)
    libelle = Column(String)
    montant = Column(Float, default=0.0)
    date = Column(String)

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, index=True)
    expediteur = Column(String, nullable=True)
    destinataire = Column(String, nullable=True)
    sujet = Column(String, nullable=True)
    contenu = Column(String)
    date = Column(String)

class Evaluation(Base):
    __tablename__ = 'evaluations'
    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String)
    classe_id = Column(Integer, ForeignKey('classes.id'))
    matiere_id = Column(Integer, ForeignKey('matieres.id'))
    date = Column(String)
    semestre = Column(Integer, default=1)
    
    classe = relationship("Classe")
    matiere = relationship("Matiere")

class EmploiDuTemps(Base):
    __tablename__ = 'emploi_du_temps'
    id = Column(Integer, primary_key=True, index=True)
    classe_id = Column(Integer, ForeignKey('classes.id'))
    matiere_id = Column(Integer, ForeignKey('matieres.id'))
    enseignant_id = Column(Integer, ForeignKey('enseignants.id'))
    jour = Column(String)
    heure = Column(String)
    semestre = Column(Integer, default=1)
    
    classe = relationship("Classe")
    matiere = relationship("Matiere")
    enseignant = relationship("Enseignant")

class CahierTexte(Base):
    __tablename__ = 'cahier_texte'
    id = Column(Integer, primary_key=True, index=True)
    classe_id = Column(Integer, ForeignKey('classes.id'))
    matiere_id = Column(Integer, ForeignKey('matieres.id'))
    enseignant_id = Column(Integer, ForeignKey('enseignants.id'))
    date = Column(String)
    contenu = Column(String)
    semestre = Column(Integer, default=1)
    
    classe = relationship("Classe")
    matiere = relationship("Matiere")
    enseignant = relationship("Enseignant")

class Note(Base):
    __tablename__ = 'notes'
    id = Column(Integer, primary_key=True, index=True)
    eleve_id = Column(Integer, ForeignKey('eleves.id'))
    matiere_id = Column(Integer, ForeignKey('matieres.id'))
    note_classe = Column(Float, default=0.0)
    note_compo = Column(Float, default=0.0)
    semestre = Column(Integer, default=1)
    
    eleve = relationship("Eleve")
    matiere = relationship("Matiere")

class Presence(Base):
    __tablename__ = 'presences'
    id = Column(Integer, primary_key=True, index=True)
    eleve_id = Column(Integer, ForeignKey('eleves.id'))
    date = Column(String)
    statut = Column(String)  # Présent, Absent, Retard
    
    eleve = relationship("Eleve")

class LogActivite(Base):
    __tablename__ = 'logs_activite'
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)
    utilisateur = Column(String)
    action = Column(String)
    details = Column(String)

class EcheancePaiement(Base):
    __tablename__ = 'echeances_paiement'
    id = Column(Integer, primary_key=True, index=True)
    eleve_id = Column(Integer, ForeignKey('eleves.id'))
    libelle = Column(String, default="Scolarité")
    montant = Column(Float, default=0.0)
    montant_total = Column(Float, default=0.0)
    montant_paye = Column(Float, default=0.0)
    
    eleve = relationship("Eleve")

class PaiementDetail(Base):
    __tablename__ = 'paiements_details'
    id = Column(Integer, primary_key=True, index=True)
    echeance_id = Column(Integer, ForeignKey('echeances_paiement.id'))
    eleve_id = Column(Integer, ForeignKey('eleves.id'))
    montant = Column(Float, default=0.0)
    date = Column(String)
    mode = Column(String)
    
    eleve = relationship("Eleve")