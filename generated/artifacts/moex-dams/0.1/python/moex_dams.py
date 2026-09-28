# Auto generated from moex-dams.yaml by pythongen.py version: 0.0.1
# Generation date: 2026-09-28T15:17:09
# Schema: moex_dams
#
# id: https://data.moex.com/dams/v0.1
# description:
# license: https://www.apache.org/licenses/LICENSE-2.0

import dataclasses
import re
from dataclasses import dataclass
from datetime import (
    date,
    datetime,
    time
)
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Optional,
    Union
)

from jsonasobj2 import (
    JsonObj,
    as_dict
)
from linkml_runtime.linkml_model.meta import (
    EnumDefinition,
    PermissibleValue,
    PvFormulaOptions
)
from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_runtime.utils.enumerations import EnumDefinitionImpl
from linkml_runtime.utils.formatutils import (
    camelcase,
    sfx,
    underscore
)
from linkml_runtime.utils.metamodelcore import (
    bnode,
    empty_dict,
    empty_list
)
from linkml_runtime.utils.slot import Slot
from linkml_runtime.utils.yamlutils import (
    YAMLRoot,
    extended_float,
    extended_int,
    extended_str
)
from rdflib import (
    Namespace,
    URIRef
)

from linkml_runtime.linkml_model.types import Boolean, Datetime, Decimal, Integer, String, Uri, Uriorcurie
from linkml_runtime.utils.metamodelcore import Bool, Decimal, URI, URIorCURIE, XSDDateTime

metamodel_version = "1.11.0"
version = "0.1.0"

# Namespaces
DAMS = CurieNamespace('dams', 'https://data.moex.com/dams/')
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
MOEX = CurieNamespace('moex', 'https://data.moex.com/')
XSD = CurieNamespace('xsd', 'http://www.w3.org/2001/XMLSchema#')
DEFAULT_ = DAMS


# Types
class SemVer(String):
    type_class_uri = XSD["string"]
    type_class_curie = "xsd:string"
    type_name = "SemVer"
    type_model_uri = DAMS.SemVer


class Sha256Digest(String):
    type_class_uri = XSD["string"]
    type_class_curie = "xsd:string"
    type_name = "Sha256Digest"
    type_model_uri = DAMS.Sha256Digest


# Class references
class MOEXModelRepositoryRepositoryId(URIorCURIE):
    pass


class RegistryEntryRegistryId(URIorCURIE):
    pass


class ITSystemRegistryId(RegistryEntryRegistryId):
    pass


class ITSolutionRegistryId(RegistryEntryRegistryId):
    pass


class ITPlatformRegistryId(RegistryEntryRegistryId):
    pass


class BusinessDomainRegistryId(RegistryEntryRegistryId):
    pass


class GlossaryTermRegistryId(RegistryEntryRegistryId):
    pass


class OrganizationUnitRegistryId(RegistryEntryRegistryId):
    pass


class RoleRegistryId(RegistryEntryRegistryId):
    pass


class DataClassificationTermRegistryId(RegistryEntryRegistryId):
    pass


class PolicyRegistryId(RegistryEntryRegistryId):
    pass


class BusinessProcessRegistryId(RegistryEntryRegistryId):
    pass


class DataContractReferenceRegistryId(RegistryEntryRegistryId):
    pass


class IntegrationReferenceRegistryId(RegistryEntryRegistryId):
    pass


class ClassificationAssignmentAssignmentId(URIorCURIE):
    pass


class PolicyBindingPolicyBindingId(URIorCURIE):
    pass


class ModelElementElementId(URIorCURIE):
    pass


class ModelPackageElementId(ModelElementElementId):
    pass


class DomainContextElementId(ModelElementElementId):
    pass


class ConceptualEntityElementId(ModelElementElementId):
    pass


class LogicalEntityElementId(ModelElementElementId):
    pass


class LogicalAttributeElementId(ModelElementElementId):
    pass


class RelationshipElementId(ModelElementElementId):
    pass


class PhysicalObjectElementId(ModelElementElementId):
    pass


class PhysicalFieldElementId(ModelElementElementId):
    pass


class MappingElementId(ModelElementElementId):
    pass


class DataFlowElementId(ModelElementElementId):
    pass


class DataFlowEntityBindingElementId(ModelElementElementId):
    pass


class DataModelBindingElementId(ModelElementElementId):
    pass


class ModelSelectionElementId(ModelElementElementId):
    pass


class SelectedEntityElementId(ModelElementElementId):
    pass


class SelectedAttributeElementId(ModelElementElementId):
    pass


class MetricElementId(ModelElementElementId):
    pass


class DimensionElementId(ModelElementElementId):
    pass


class FormalCheckCheckId(extended_str):
    pass


class SpecificationRequirementElementId(ModelElementElementId):
    pass


class RequirementCatalogCatalogId(URIorCURIE):
    pass


@dataclass(repr=False)
class MOEXModelRepository(YAMLRoot):
    """
    Корневой контейнер для проверки набора моделей, ссылочных проекций справочников, потоков и контрактных bindings.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["MOEXModelRepository"]
    class_class_curie: ClassVar[str] = "dams:MOEXModelRepository"
    class_name: ClassVar[str] = "MOEXModelRepository"
    class_model_uri: ClassVar[URIRef] = DAMS.MOEXModelRepository

    repository_id: Union[str, MOEXModelRepositoryRepositoryId] = None
    registry_entries: Optional[Union[dict[Union[str, RegistryEntryRegistryId], Union[dict, "RegistryEntry"]], list[Union[dict, "RegistryEntry"]]]] = empty_dict()
    model_packages: Optional[Union[dict[Union[str, ModelPackageElementId], Union[dict, "ModelPackage"]], list[Union[dict, "ModelPackage"]]]] = empty_dict()
    data_flows: Optional[Union[dict[Union[str, DataFlowElementId], Union[dict, "DataFlow"]], list[Union[dict, "DataFlow"]]]] = empty_dict()
    data_model_bindings: Optional[Union[dict[Union[str, DataModelBindingElementId], Union[dict, "DataModelBinding"]], list[Union[dict, "DataModelBinding"]]]] = empty_dict()
    metrics: Optional[Union[dict[Union[str, MetricElementId], Union[dict, "Metric"]], list[Union[dict, "Metric"]]]] = empty_dict()
    dimensions: Optional[Union[dict[Union[str, DimensionElementId], Union[dict, "Dimension"]], list[Union[dict, "Dimension"]]]] = empty_dict()
    classification_assignments: Optional[Union[dict[Union[str, ClassificationAssignmentAssignmentId], Union[dict, "ClassificationAssignment"]], list[Union[dict, "ClassificationAssignment"]]]] = empty_dict()
    policy_bindings: Optional[Union[dict[Union[str, PolicyBindingPolicyBindingId], Union[dict, "PolicyBinding"]], list[Union[dict, "PolicyBinding"]]]] = empty_dict()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.repository_id):
            self.MissingRequiredField("repository_id")
        if not isinstance(self.repository_id, MOEXModelRepositoryRepositoryId):
            self.repository_id = MOEXModelRepositoryRepositoryId(self.repository_id)

        self._normalize_inlined_as_list(slot_name="registry_entries", slot_type=RegistryEntry, key_name="registry_id", keyed=True)

        self._normalize_inlined_as_list(slot_name="model_packages", slot_type=ModelPackage, key_name="element_id", keyed=True)

        self._normalize_inlined_as_list(slot_name="data_flows", slot_type=DataFlow, key_name="element_id", keyed=True)

        self._normalize_inlined_as_list(slot_name="data_model_bindings", slot_type=DataModelBinding, key_name="element_id", keyed=True)

        self._normalize_inlined_as_list(slot_name="metrics", slot_type=Metric, key_name="element_id", keyed=True)

        self._normalize_inlined_as_list(slot_name="dimensions", slot_type=Dimension, key_name="element_id", keyed=True)

        self._normalize_inlined_as_list(slot_name="classification_assignments", slot_type=ClassificationAssignment, key_name="assignment_id", keyed=True)

        self._normalize_inlined_as_list(slot_name="policy_bindings", slot_type=PolicyBinding, key_name="policy_binding_id", keyed=True)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class RegistryEntry(YAMLRoot):
    """
    Локальная ссылочная проекция записи внешней мастер-системы; не является мастер-копией справочника.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["RegistryEntry"]
    class_class_curie: ClassVar[str] = "dams:RegistryEntry"
    class_name: ClassVar[str] = "RegistryEntry"
    class_model_uri: ClassVar[URIRef] = DAMS.RegistryEntry

    registry_id: Union[str, RegistryEntryRegistryId] = None
    registry_name: str = None
    master_system: str = None
    registry_status: Union[str, "LifecycleStatusEnum"] = None
    registry_description: Optional[str] = None
    source_uri: Optional[Union[str, URI]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.registry_id):
            self.MissingRequiredField("registry_id")
        if not isinstance(self.registry_id, RegistryEntryRegistryId):
            self.registry_id = RegistryEntryRegistryId(self.registry_id)

        if self._is_empty(self.registry_name):
            self.MissingRequiredField("registry_name")
        if not isinstance(self.registry_name, str):
            self.registry_name = str(self.registry_name)

        if self._is_empty(self.master_system):
            self.MissingRequiredField("master_system")
        if not isinstance(self.master_system, str):
            self.master_system = str(self.master_system)

        if self._is_empty(self.registry_status):
            self.MissingRequiredField("registry_status")
        if not isinstance(self.registry_status, LifecycleStatusEnum):
            self.registry_status = LifecycleStatusEnum(self.registry_status)

        if self.registry_description is not None and not isinstance(self.registry_description, str):
            self.registry_description = str(self.registry_description)

        if self.source_uri is not None and not isinstance(self.source_uri, URI):
            self.source_uri = URI(self.source_uri)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ITSystem(RegistryEntry):
    """
    ИТ-система; мастер данных — EAM.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["ITSystem"]
    class_class_curie: ClassVar[str] = "dams:ITSystem"
    class_name: ClassVar[str] = "ITSystem"
    class_model_uri: ClassVar[URIRef] = DAMS.ITSystem

    registry_id: Union[str, ITSystemRegistryId] = None
    registry_name: str = None
    master_system: str = None
    registry_status: Union[str, "LifecycleStatusEnum"] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.registry_id):
            self.MissingRequiredField("registry_id")
        if not isinstance(self.registry_id, ITSystemRegistryId):
            self.registry_id = ITSystemRegistryId(self.registry_id)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ITSolution(RegistryEntry):
    """
    ИТ-решение, объединяющее одну или несколько ИТ-систем; мастер данных — EAM.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["ITSolution"]
    class_class_curie: ClassVar[str] = "dams:ITSolution"
    class_name: ClassVar[str] = "ITSolution"
    class_model_uri: ClassVar[URIRef] = DAMS.ITSolution

    registry_id: Union[str, ITSolutionRegistryId] = None
    registry_name: str = None
    master_system: str = None
    registry_status: Union[str, "LifecycleStatusEnum"] = None
    member_system_refs: Optional[Union[Union[str, ITSystemRegistryId], list[Union[str, ITSystemRegistryId]]]] = empty_list()
    platform_ref: Optional[Union[str, ITPlatformRegistryId]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.registry_id):
            self.MissingRequiredField("registry_id")
        if not isinstance(self.registry_id, ITSolutionRegistryId):
            self.registry_id = ITSolutionRegistryId(self.registry_id)

        if not isinstance(self.member_system_refs, list):
            self.member_system_refs = [self.member_system_refs] if self.member_system_refs is not None else []
        self.member_system_refs = [v if isinstance(v, ITSystemRegistryId) else ITSystemRegistryId(v) for v in self.member_system_refs]

        if self.platform_ref is not None and not isinstance(self.platform_ref, ITPlatformRegistryId):
            self.platform_ref = ITPlatformRegistryId(self.platform_ref)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ITPlatform(RegistryEntry):
    """
    ИТ-платформа; мастер данных — EAM.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["ITPlatform"]
    class_class_curie: ClassVar[str] = "dams:ITPlatform"
    class_name: ClassVar[str] = "ITPlatform"
    class_model_uri: ClassVar[URIRef] = DAMS.ITPlatform

    registry_id: Union[str, ITPlatformRegistryId] = None
    registry_name: str = None
    master_system: str = None
    registry_status: Union[str, "LifecycleStatusEnum"] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.registry_id):
            self.MissingRequiredField("registry_id")
        if not isinstance(self.registry_id, ITPlatformRegistryId):
            self.registry_id = ITPlatformRegistryId(self.registry_id)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class BusinessDomain(RegistryEntry):
    """
    Бизнес-домен или предметная область; мастер определяется архитектурным governance.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["BusinessDomain"]
    class_class_curie: ClassVar[str] = "dams:BusinessDomain"
    class_name: ClassVar[str] = "BusinessDomain"
    class_model_uri: ClassVar[URIRef] = DAMS.BusinessDomain

    registry_id: Union[str, BusinessDomainRegistryId] = None
    registry_name: str = None
    master_system: str = None
    registry_status: Union[str, "LifecycleStatusEnum"] = None
    parent_domain_ref: Optional[Union[str, BusinessDomainRegistryId]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.registry_id):
            self.MissingRequiredField("registry_id")
        if not isinstance(self.registry_id, BusinessDomainRegistryId):
            self.registry_id = BusinessDomainRegistryId(self.registry_id)

        if self.parent_domain_ref is not None and not isinstance(self.parent_domain_ref, BusinessDomainRegistryId):
            self.parent_domain_ref = BusinessDomainRegistryId(self.parent_domain_ref)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class GlossaryTerm(RegistryEntry):
    """
    Термин корпоративного бизнес-глоссария.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["GlossaryTerm"]
    class_class_curie: ClassVar[str] = "dams:GlossaryTerm"
    class_name: ClassVar[str] = "GlossaryTerm"
    class_model_uri: ClassVar[URIRef] = DAMS.GlossaryTerm

    registry_id: Union[str, GlossaryTermRegistryId] = None
    registry_name: str = None
    master_system: str = None
    registry_status: Union[str, "LifecycleStatusEnum"] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.registry_id):
            self.MissingRequiredField("registry_id")
        if not isinstance(self.registry_id, GlossaryTermRegistryId):
            self.registry_id = GlossaryTermRegistryId(self.registry_id)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class OrganizationUnit(RegistryEntry):
    """
    Организационное подразделение.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["OrganizationUnit"]
    class_class_curie: ClassVar[str] = "dams:OrganizationUnit"
    class_name: ClassVar[str] = "OrganizationUnit"
    class_model_uri: ClassVar[URIRef] = DAMS.OrganizationUnit

    registry_id: Union[str, OrganizationUnitRegistryId] = None
    registry_name: str = None
    master_system: str = None
    registry_status: Union[str, "LifecycleStatusEnum"] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.registry_id):
            self.MissingRequiredField("registry_id")
        if not isinstance(self.registry_id, OrganizationUnitRegistryId):
            self.registry_id = OrganizationUnitRegistryId(self.registry_id)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Role(RegistryEntry):
    """
    Управляемая роль владельца, стюарда, потребителя или согласующего.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["Role"]
    class_class_curie: ClassVar[str] = "dams:Role"
    class_name: ClassVar[str] = "Role"
    class_model_uri: ClassVar[URIRef] = DAMS.Role

    registry_id: Union[str, RoleRegistryId] = None
    registry_name: str = None
    master_system: str = None
    registry_status: Union[str, "LifecycleStatusEnum"] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.registry_id):
            self.MissingRequiredField("registry_id")
        if not isinstance(self.registry_id, RoleRegistryId):
            self.registry_id = RoleRegistryId(self.registry_id)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class DataClassificationTerm(RegistryEntry):
    """
    Специальная категория чувствительности или регулирования, например ПДн или инсайдерская информация.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["DataClassificationTerm"]
    class_class_curie: ClassVar[str] = "dams:DataClassificationTerm"
    class_name: ClassVar[str] = "DataClassificationTerm"
    class_model_uri: ClassVar[URIRef] = DAMS.DataClassificationTerm

    registry_id: Union[str, DataClassificationTermRegistryId] = None
    registry_name: str = None
    master_system: str = None
    registry_status: Union[str, "LifecycleStatusEnum"] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.registry_id):
            self.MissingRequiredField("registry_id")
        if not isinstance(self.registry_id, DataClassificationTermRegistryId):
            self.registry_id = DataClassificationTermRegistryId(self.registry_id)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Policy(RegistryEntry):
    """
    Политика доступа, хранения, качества или архитектурный инвариант.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["Policy"]
    class_class_curie: ClassVar[str] = "dams:Policy"
    class_name: ClassVar[str] = "Policy"
    class_model_uri: ClassVar[URIRef] = DAMS.Policy

    registry_id: Union[str, PolicyRegistryId] = None
    registry_name: str = None
    master_system: str = None
    registry_status: Union[str, "LifecycleStatusEnum"] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.registry_id):
            self.MissingRequiredField("registry_id")
        if not isinstance(self.registry_id, PolicyRegistryId):
            self.registry_id = PolicyRegistryId(self.registry_id)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class BusinessProcess(RegistryEntry):
    """
    Ссылка на бизнес-процесс или его шаг в BPMN-репозитории.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["BusinessProcess"]
    class_class_curie: ClassVar[str] = "dams:BusinessProcess"
    class_name: ClassVar[str] = "BusinessProcess"
    class_model_uri: ClassVar[URIRef] = DAMS.BusinessProcess

    registry_id: Union[str, BusinessProcessRegistryId] = None
    registry_name: str = None
    master_system: str = None
    registry_status: Union[str, "LifecycleStatusEnum"] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.registry_id):
            self.MissingRequiredField("registry_id")
        if not isinstance(self.registry_id, BusinessProcessRegistryId):
            self.registry_id = BusinessProcessRegistryId(self.registry_id)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class DataContractReference(RegistryEntry):
    """
    Ссылка на дата-контракт в корпоративном дата-каталоге.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["DataContractReference"]
    class_class_curie: ClassVar[str] = "dams:DataContractReference"
    class_name: ClassVar[str] = "DataContractReference"
    class_model_uri: ClassVar[URIRef] = DAMS.DataContractReference

    registry_id: Union[str, DataContractReferenceRegistryId] = None
    registry_name: str = None
    master_system: str = None
    registry_status: Union[str, "LifecycleStatusEnum"] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.registry_id):
            self.MissingRequiredField("registry_id")
        if not isinstance(self.registry_id, DataContractReferenceRegistryId):
            self.registry_id = DataContractReferenceRegistryId(self.registry_id)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class IntegrationReference(RegistryEntry):
    """
    Ссылка на интеграцию в Clinkr.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["IntegrationReference"]
    class_class_curie: ClassVar[str] = "dams:IntegrationReference"
    class_name: ClassVar[str] = "IntegrationReference"
    class_model_uri: ClassVar[URIRef] = DAMS.IntegrationReference

    registry_id: Union[str, IntegrationReferenceRegistryId] = None
    registry_name: str = None
    master_system: str = None
    registry_status: Union[str, "LifecycleStatusEnum"] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.registry_id):
            self.MissingRequiredField("registry_id")
        if not isinstance(self.registry_id, IntegrationReferenceRegistryId):
            self.registry_id = IntegrationReferenceRegistryId(self.registry_id)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ClassificationAssignment(YAMLRoot):
    """
    Версионируемое назначение категории классификации элементу модели с основанием и периодом действия.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["ClassificationAssignment"]
    class_class_curie: ClassVar[str] = "dams:ClassificationAssignment"
    class_name: ClassVar[str] = "ClassificationAssignment"
    class_model_uri: ClassVar[URIRef] = DAMS.ClassificationAssignment

    assignment_id: Union[str, ClassificationAssignmentAssignmentId] = None
    classified_element_ref: Union[str, URIorCURIE] = None
    classification_term_ref: Optional[Union[str, DataClassificationTermRegistryId]] = None
    governance_classification: Optional[Union[str, "GovernanceClassificationEnum"]] = None
    classification_source: Optional[str] = None
    classification_rationale: Optional[str] = None
    valid_from: Optional[Union[str, XSDDateTime]] = None
    valid_to: Optional[Union[str, XSDDateTime]] = None
    approval_status: Optional[Union[str, "ApprovalStatusEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.assignment_id):
            self.MissingRequiredField("assignment_id")
        if not isinstance(self.assignment_id, ClassificationAssignmentAssignmentId):
            self.assignment_id = ClassificationAssignmentAssignmentId(self.assignment_id)

        if self._is_empty(self.classified_element_ref):
            self.MissingRequiredField("classified_element_ref")
        if not isinstance(self.classified_element_ref, URIorCURIE):
            self.classified_element_ref = URIorCURIE(self.classified_element_ref)

        if self.classification_term_ref is not None and not isinstance(self.classification_term_ref, DataClassificationTermRegistryId):
            self.classification_term_ref = DataClassificationTermRegistryId(self.classification_term_ref)

        if self.governance_classification is not None and not isinstance(self.governance_classification, GovernanceClassificationEnum):
            self.governance_classification = GovernanceClassificationEnum(self.governance_classification)

        if self.classification_source is not None and not isinstance(self.classification_source, str):
            self.classification_source = str(self.classification_source)

        if self.classification_rationale is not None and not isinstance(self.classification_rationale, str):
            self.classification_rationale = str(self.classification_rationale)

        if self.valid_from is not None and not isinstance(self.valid_from, XSDDateTime):
            self.valid_from = XSDDateTime(self.valid_from)

        if self.valid_to is not None and not isinstance(self.valid_to, XSDDateTime):
            self.valid_to = XSDDateTime(self.valid_to)

        if self.approval_status is not None and not isinstance(self.approval_status, ApprovalStatusEnum):
            self.approval_status = ApprovalStatusEnum(self.approval_status)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class PolicyBinding(YAMLRoot):
    """
    Применение управляемой политики к элементу модели.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["PolicyBinding"]
    class_class_curie: ClassVar[str] = "dams:PolicyBinding"
    class_name: ClassVar[str] = "PolicyBinding"
    class_model_uri: ClassVar[URIRef] = DAMS.PolicyBinding

    policy_binding_id: Union[str, PolicyBindingPolicyBindingId] = None
    policy_target_ref: Union[str, URIorCURIE] = None
    policy_ref: Union[str, PolicyRegistryId] = None
    valid_from: Optional[Union[str, XSDDateTime]] = None
    valid_to: Optional[Union[str, XSDDateTime]] = None
    approval_status: Optional[Union[str, "ApprovalStatusEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.policy_binding_id):
            self.MissingRequiredField("policy_binding_id")
        if not isinstance(self.policy_binding_id, PolicyBindingPolicyBindingId):
            self.policy_binding_id = PolicyBindingPolicyBindingId(self.policy_binding_id)

        if self._is_empty(self.policy_target_ref):
            self.MissingRequiredField("policy_target_ref")
        if not isinstance(self.policy_target_ref, URIorCURIE):
            self.policy_target_ref = URIorCURIE(self.policy_target_ref)

        if self._is_empty(self.policy_ref):
            self.MissingRequiredField("policy_ref")
        if not isinstance(self.policy_ref, PolicyRegistryId):
            self.policy_ref = PolicyRegistryId(self.policy_ref)

        if self.valid_from is not None and not isinstance(self.valid_from, XSDDateTime):
            self.valid_from = XSDDateTime(self.valid_from)

        if self.valid_to is not None and not isinstance(self.valid_to, XSDDateTime):
            self.valid_to = XSDDateTime(self.valid_to)

        if self.approval_status is not None and not isinstance(self.approval_status, ApprovalStatusEnum):
            self.approval_status = ApprovalStatusEnum(self.approval_status)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class HasLifecycle(YAMLRoot):
    """
    Mixin жизненного цикла: статус, период действия и ссылка на заменяющий элемент.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["HasLifecycle"]
    class_class_curie: ClassVar[str] = "dams:HasLifecycle"
    class_name: ClassVar[str] = "HasLifecycle"
    class_model_uri: ClassVar[URIRef] = DAMS.HasLifecycle

    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    valid_from: Optional[Union[str, XSDDateTime]] = None
    valid_to: Optional[Union[str, XSDDateTime]] = None
    deprecated_by_ref: Optional[Union[str, URIorCURIE]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.lifecycle_status):
            self.MissingRequiredField("lifecycle_status")
        if not isinstance(self.lifecycle_status, LifecycleStatusEnum):
            self.lifecycle_status = LifecycleStatusEnum(self.lifecycle_status)

        if self.valid_from is not None and not isinstance(self.valid_from, XSDDateTime):
            self.valid_from = XSDDateTime(self.valid_from)

        if self.valid_to is not None and not isinstance(self.valid_to, XSDDateTime):
            self.valid_to = XSDDateTime(self.valid_to)

        if self.deprecated_by_ref is not None and not isinstance(self.deprecated_by_ref, URIorCURIE):
            self.deprecated_by_ref = URIorCURIE(self.deprecated_by_ref)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class HasOwnership(YAMLRoot):
    """
    Mixin владения: data owner, data steward и организационное подразделение.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["HasOwnership"]
    class_class_curie: ClassVar[str] = "dams:HasOwnership"
    class_name: ClassVar[str] = "HasOwnership"
    class_model_uri: ClassVar[URIRef] = DAMS.HasOwnership

    data_owner_ref: Optional[Union[str, RoleRegistryId]] = None
    data_steward_ref: Optional[Union[str, RoleRegistryId]] = None
    owning_unit_ref: Optional[Union[str, OrganizationUnitRegistryId]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.data_owner_ref is not None and not isinstance(self.data_owner_ref, RoleRegistryId):
            self.data_owner_ref = RoleRegistryId(self.data_owner_ref)

        if self.data_steward_ref is not None and not isinstance(self.data_steward_ref, RoleRegistryId):
            self.data_steward_ref = RoleRegistryId(self.data_steward_ref)

        if self.owning_unit_ref is not None and not isinstance(self.owning_unit_ref, OrganizationUnitRegistryId):
            self.owning_unit_ref = OrganizationUnitRegistryId(self.owning_unit_ref)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class HasBusinessClassification(YAMLRoot):
    """
    Классификация роли и бизнес-значимости логической сущности.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["HasBusinessClassification"]
    class_class_curie: ClassVar[str] = "dams:HasBusinessClassification"
    class_name: ClassVar[str] = "HasBusinessClassification"
    class_model_uri: ClassVar[URIRef] = DAMS.HasBusinessClassification

    entity_type: Optional[Union[str, "EntityTypeEnum"]] = None
    data_class: Optional[Union[str, "DataClassEnum"]] = None
    business_importance: Optional[Union[str, "BusinessImportanceEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.entity_type is not None and not isinstance(self.entity_type, EntityTypeEnum):
            self.entity_type = EntityTypeEnum(self.entity_type)

        if self.data_class is not None and not isinstance(self.data_class, DataClassEnum):
            self.data_class = DataClassEnum(self.data_class)

        if self.business_importance is not None and not isinstance(self.business_importance, BusinessImportanceEnum):
            self.business_importance = BusinessImportanceEnum(self.business_importance)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class HasGovernanceClassification(YAMLRoot):
    """
    Базовая и специальная классификация чувствительности данных.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["HasGovernanceClassification"]
    class_class_curie: ClassVar[str] = "dams:HasGovernanceClassification"
    class_name: ClassVar[str] = "HasGovernanceClassification"
    class_model_uri: ClassVar[URIRef] = DAMS.HasGovernanceClassification

    governance_classification: Optional[Union[str, "GovernanceClassificationEnum"]] = None
    sensitivity_term_refs: Optional[Union[Union[str, DataClassificationTermRegistryId], list[Union[str, DataClassificationTermRegistryId]]]] = empty_list()
    classification_source: Optional[str] = None
    classification_rationale: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.governance_classification is not None and not isinstance(self.governance_classification, GovernanceClassificationEnum):
            self.governance_classification = GovernanceClassificationEnum(self.governance_classification)

        if not isinstance(self.sensitivity_term_refs, list):
            self.sensitivity_term_refs = [self.sensitivity_term_refs] if self.sensitivity_term_refs is not None else []
        self.sensitivity_term_refs = [v if isinstance(v, DataClassificationTermRegistryId) else DataClassificationTermRegistryId(v) for v in self.sensitivity_term_refs]

        if self.classification_source is not None and not isinstance(self.classification_source, str):
            self.classification_source = str(self.classification_source)

        if self.classification_rationale is not None and not isinstance(self.classification_rationale, str):
            self.classification_rationale = str(self.classification_rationale)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class HasPolicyBindings(YAMLRoot):
    """
    Mixin привязки управляемых политик к элементу модели.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["HasPolicyBindings"]
    class_class_curie: ClassVar[str] = "dams:HasPolicyBindings"
    class_name: ClassVar[str] = "HasPolicyBindings"
    class_model_uri: ClassVar[URIRef] = DAMS.HasPolicyBindings

    policy_refs: Optional[Union[Union[str, PolicyRegistryId], list[Union[str, PolicyRegistryId]]]] = empty_list()

    def __post_init__(self, *_: str, **kwargs: Any):
        if not isinstance(self.policy_refs, list):
            self.policy_refs = [self.policy_refs] if self.policy_refs is not None else []
        self.policy_refs = [v if isinstance(v, PolicyRegistryId) else PolicyRegistryId(v) for v in self.policy_refs]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class HasProvenance(YAMLRoot):
    """
    Mixin происхождения и согласования: исходный артефакт, evidence, статус и согласующий.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["HasProvenance"]
    class_class_curie: ClassVar[str] = "dams:HasProvenance"
    class_name: ClassVar[str] = "HasProvenance"
    class_model_uri: ClassVar[URIRef] = DAMS.HasProvenance

    source_artifact_ref: Optional[Union[str, URI]] = None
    evidence_refs: Optional[Union[Union[str, URI], list[Union[str, URI]]]] = empty_list()
    approval_status: Optional[Union[str, "ApprovalStatusEnum"]] = None
    approved_by_ref: Optional[Union[str, RoleRegistryId]] = None
    approved_at: Optional[Union[str, XSDDateTime]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.source_artifact_ref is not None and not isinstance(self.source_artifact_ref, URI):
            self.source_artifact_ref = URI(self.source_artifact_ref)

        if not isinstance(self.evidence_refs, list):
            self.evidence_refs = [self.evidence_refs] if self.evidence_refs is not None else []
        self.evidence_refs = [v if isinstance(v, URI) else URI(v) for v in self.evidence_refs]

        if self.approval_status is not None and not isinstance(self.approval_status, ApprovalStatusEnum):
            self.approval_status = ApprovalStatusEnum(self.approval_status)

        if self.approved_by_ref is not None and not isinstance(self.approved_by_ref, RoleRegistryId):
            self.approved_by_ref = RoleRegistryId(self.approved_by_ref)

        if self.approved_at is not None and not isinstance(self.approved_at, XSDDateTime):
            self.approved_at = XSDDateTime(self.approved_at)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ModelElement(YAMLRoot):
    """
    Абстрактный корень иерархии элементов модели: общая идентичность (element_id), имя, описание и жизненный цикл.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["ModelElement"]
    class_class_curie: ClassVar[str] = "dams:ModelElement"
    class_name: ClassVar[str] = "ModelElement"
    class_model_uri: ClassVar[URIRef] = DAMS.ModelElement

    element_id: Union[str, ModelElementElementId] = None
    name: str = None
    description: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    title: Optional[str] = None
    aliases: Optional[Union[str, list[str]]] = empty_list()
    glossary_term_refs: Optional[Union[Union[str, GlossaryTermRegistryId], list[Union[str, GlossaryTermRegistryId]]]] = empty_list()
    tags: Optional[Union[str, list[str]]] = empty_list()
    valid_from: Optional[Union[str, XSDDateTime]] = None
    valid_to: Optional[Union[str, XSDDateTime]] = None
    deprecated_by_ref: Optional[Union[str, URIorCURIE]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, ModelElementElementId):
            self.element_id = ModelElementElementId(self.element_id)

        if self._is_empty(self.name):
            self.MissingRequiredField("name")
        if not isinstance(self.name, str):
            self.name = str(self.name)

        if self._is_empty(self.description):
            self.MissingRequiredField("description")
        if not isinstance(self.description, str):
            self.description = str(self.description)

        if self._is_empty(self.lifecycle_status):
            self.MissingRequiredField("lifecycle_status")
        if not isinstance(self.lifecycle_status, LifecycleStatusEnum):
            self.lifecycle_status = LifecycleStatusEnum(self.lifecycle_status)

        if self.title is not None and not isinstance(self.title, str):
            self.title = str(self.title)

        if not isinstance(self.aliases, list):
            self.aliases = [self.aliases] if self.aliases is not None else []
        self.aliases = [v if isinstance(v, str) else str(v) for v in self.aliases]

        if not isinstance(self.glossary_term_refs, list):
            self.glossary_term_refs = [self.glossary_term_refs] if self.glossary_term_refs is not None else []
        self.glossary_term_refs = [v if isinstance(v, GlossaryTermRegistryId) else GlossaryTermRegistryId(v) for v in self.glossary_term_refs]

        if not isinstance(self.tags, list):
            self.tags = [self.tags] if self.tags is not None else []
        self.tags = [v if isinstance(v, str) else str(v) for v in self.tags]

        if self.valid_from is not None and not isinstance(self.valid_from, XSDDateTime):
            self.valid_from = XSDDateTime(self.valid_from)

        if self.valid_to is not None and not isinstance(self.valid_to, XSDDateTime):
            self.valid_to = XSDDateTime(self.valid_to)

        if self.deprecated_by_ref is not None and not isinstance(self.deprecated_by_ref, URIorCURIE):
            self.deprecated_by_ref = URIorCURIE(self.deprecated_by_ref)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ModelPackage(ModelElement):
    """
    Версионируемый артефакт модели данных: либо корпоративная conceptual модель (enterprise), либо модель конкретного
    ИТ-решения (solution). Package-level DAMS layer is dams_model_level on the SpecImpl envelope (ADR-021);
    implementation_scope here mirrors that body-level semantics.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["ModelPackage"]
    class_class_curie: ClassVar[str] = "dams:ModelPackage"
    class_name: ClassVar[str] = "ModelPackage"
    class_model_uri: ClassVar[URIRef] = DAMS.ModelPackage

    element_id: Union[str, ModelPackageElementId] = None
    name: str = None
    description: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    api_version: str = None
    model_version: Union[str, SemVer] = None
    implementation_scope: Optional[Union[str, "ImplementationScopeEnum"]] = None
    conceptual_implementation_ref: Optional[Union[str, URIorCURIE]] = None
    solution_ref: Optional[Union[str, ITSolutionRegistryId]] = None
    domain_refs: Optional[Union[Union[str, BusinessDomainRegistryId], list[Union[str, BusinessDomainRegistryId]]]] = empty_list()
    imports_refs: Optional[Union[Union[str, URI], list[Union[str, URI]]]] = empty_list()
    conceptual_entities: Optional[Union[dict[Union[str, ConceptualEntityElementId], Union[dict, "ConceptualEntity"]], list[Union[dict, "ConceptualEntity"]]]] = empty_dict()
    domain_contexts: Optional[Union[dict[Union[str, DomainContextElementId], Union[dict, "DomainContext"]], list[Union[dict, "DomainContext"]]]] = empty_dict()
    logical_entities: Optional[Union[dict[Union[str, LogicalEntityElementId], Union[dict, "LogicalEntity"]], list[Union[dict, "LogicalEntity"]]]] = empty_dict()
    relationships: Optional[Union[dict[Union[str, RelationshipElementId], Union[dict, "Relationship"]], list[Union[dict, "Relationship"]]]] = empty_dict()
    physical_objects: Optional[Union[dict[Union[str, PhysicalObjectElementId], Union[dict, "PhysicalObject"]], list[Union[dict, "PhysicalObject"]]]] = empty_dict()
    mappings: Optional[Union[dict[Union[str, MappingElementId], Union[dict, "Mapping"]], list[Union[dict, "Mapping"]]]] = empty_dict()
    data_owner_ref: Optional[Union[str, RoleRegistryId]] = None
    data_steward_ref: Optional[Union[str, RoleRegistryId]] = None
    owning_unit_ref: Optional[Union[str, OrganizationUnitRegistryId]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, ModelPackageElementId):
            self.element_id = ModelPackageElementId(self.element_id)

        if self._is_empty(self.api_version):
            self.MissingRequiredField("api_version")
        if not isinstance(self.api_version, str):
            self.api_version = str(self.api_version)

        if self._is_empty(self.model_version):
            self.MissingRequiredField("model_version")
        if not isinstance(self.model_version, SemVer):
            self.model_version = SemVer(self.model_version)

        if self.implementation_scope is not None and not isinstance(self.implementation_scope, ImplementationScopeEnum):
            self.implementation_scope = ImplementationScopeEnum(self.implementation_scope)

        if self.conceptual_implementation_ref is not None and not isinstance(self.conceptual_implementation_ref, URIorCURIE):
            self.conceptual_implementation_ref = URIorCURIE(self.conceptual_implementation_ref)

        if self.solution_ref is not None and not isinstance(self.solution_ref, ITSolutionRegistryId):
            self.solution_ref = ITSolutionRegistryId(self.solution_ref)

        if not isinstance(self.domain_refs, list):
            self.domain_refs = [self.domain_refs] if self.domain_refs is not None else []
        self.domain_refs = [v if isinstance(v, BusinessDomainRegistryId) else BusinessDomainRegistryId(v) for v in self.domain_refs]

        if not isinstance(self.imports_refs, list):
            self.imports_refs = [self.imports_refs] if self.imports_refs is not None else []
        self.imports_refs = [v if isinstance(v, URI) else URI(v) for v in self.imports_refs]

        self._normalize_inlined_as_list(slot_name="conceptual_entities", slot_type=ConceptualEntity, key_name="element_id", keyed=True)

        self._normalize_inlined_as_list(slot_name="domain_contexts", slot_type=DomainContext, key_name="element_id", keyed=True)

        self._normalize_inlined_as_list(slot_name="logical_entities", slot_type=LogicalEntity, key_name="element_id", keyed=True)

        self._normalize_inlined_as_list(slot_name="relationships", slot_type=Relationship, key_name="element_id", keyed=True)

        self._normalize_inlined_as_list(slot_name="physical_objects", slot_type=PhysicalObject, key_name="element_id", keyed=True)

        self._normalize_inlined_as_list(slot_name="mappings", slot_type=Mapping, key_name="element_id", keyed=True)

        if self.data_owner_ref is not None and not isinstance(self.data_owner_ref, RoleRegistryId):
            self.data_owner_ref = RoleRegistryId(self.data_owner_ref)

        if self.data_steward_ref is not None and not isinstance(self.data_steward_ref, RoleRegistryId):
            self.data_steward_ref = RoleRegistryId(self.data_steward_ref)

        if self.owning_unit_ref is not None and not isinstance(self.owning_unit_ref, OrganizationUnitRegistryId):
            self.owning_unit_ref = OrganizationUnitRegistryId(self.owning_unit_ref)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class DomainContext(ModelElement):
    """
    Ограниченный логический контекст с собственной терминологией и областью ответственности.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["DomainContext"]
    class_class_curie: ClassVar[str] = "dams:DomainContext"
    class_name: ClassVar[str] = "DomainContext"
    class_model_uri: ClassVar[URIRef] = DAMS.DomainContext

    element_id: Union[str, DomainContextElementId] = None
    name: str = None
    description: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    domain_ref: Union[str, BusinessDomainRegistryId] = None
    namespace: Union[str, URI] = None
    solution_ref: Optional[Union[str, ITSolutionRegistryId]] = None
    business_process_refs: Optional[Union[Union[str, BusinessProcessRegistryId], list[Union[str, BusinessProcessRegistryId]]]] = empty_list()
    data_owner_ref: Optional[Union[str, RoleRegistryId]] = None
    data_steward_ref: Optional[Union[str, RoleRegistryId]] = None
    owning_unit_ref: Optional[Union[str, OrganizationUnitRegistryId]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, DomainContextElementId):
            self.element_id = DomainContextElementId(self.element_id)

        if self._is_empty(self.domain_ref):
            self.MissingRequiredField("domain_ref")
        if not isinstance(self.domain_ref, BusinessDomainRegistryId):
            self.domain_ref = BusinessDomainRegistryId(self.domain_ref)

        if self._is_empty(self.namespace):
            self.MissingRequiredField("namespace")
        if not isinstance(self.namespace, URI):
            self.namespace = URI(self.namespace)

        if self.solution_ref is not None and not isinstance(self.solution_ref, ITSolutionRegistryId):
            self.solution_ref = ITSolutionRegistryId(self.solution_ref)

        if not isinstance(self.business_process_refs, list):
            self.business_process_refs = [self.business_process_refs] if self.business_process_refs is not None else []
        self.business_process_refs = [v if isinstance(v, BusinessProcessRegistryId) else BusinessProcessRegistryId(v) for v in self.business_process_refs]

        if self.data_owner_ref is not None and not isinstance(self.data_owner_ref, RoleRegistryId):
            self.data_owner_ref = RoleRegistryId(self.data_owner_ref)

        if self.data_steward_ref is not None and not isinstance(self.data_steward_ref, RoleRegistryId):
            self.data_steward_ref = RoleRegistryId(self.data_steward_ref)

        if self.owning_unit_ref is not None and not isinstance(self.owning_unit_ref, OrganizationUnitRegistryId):
            self.owning_unit_ref = OrganizationUnitRegistryId(self.owning_unit_ref)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ConceptualEntity(ModelElement):
    """
    Корпоративное бизнес-понятие верхнего уровня, независимое от конкретной реализации.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["ConceptualEntity"]
    class_class_curie: ClassVar[str] = "dams:ConceptualEntity"
    class_name: ClassVar[str] = "ConceptualEntity"
    class_model_uri: ClassVar[URIRef] = DAMS.ConceptualEntity

    element_id: Union[str, ConceptualEntityElementId] = None
    name: str = None
    description: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    parent_concept_ref: Optional[Union[str, ConceptualEntityElementId]] = None
    key_attribute_refs: Optional[Union[Union[str, URIorCURIE], list[Union[str, URIorCURIE]]]] = empty_list()
    data_owner_ref: Optional[Union[str, RoleRegistryId]] = None
    data_steward_ref: Optional[Union[str, RoleRegistryId]] = None
    owning_unit_ref: Optional[Union[str, OrganizationUnitRegistryId]] = None
    entity_type: Optional[Union[str, "EntityTypeEnum"]] = None
    data_class: Optional[Union[str, "DataClassEnum"]] = None
    business_importance: Optional[Union[str, "BusinessImportanceEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, ConceptualEntityElementId):
            self.element_id = ConceptualEntityElementId(self.element_id)

        if self.parent_concept_ref is not None and not isinstance(self.parent_concept_ref, ConceptualEntityElementId):
            self.parent_concept_ref = ConceptualEntityElementId(self.parent_concept_ref)

        if not isinstance(self.key_attribute_refs, list):
            self.key_attribute_refs = [self.key_attribute_refs] if self.key_attribute_refs is not None else []
        self.key_attribute_refs = [v if isinstance(v, URIorCURIE) else URIorCURIE(v) for v in self.key_attribute_refs]

        if self.data_owner_ref is not None and not isinstance(self.data_owner_ref, RoleRegistryId):
            self.data_owner_ref = RoleRegistryId(self.data_owner_ref)

        if self.data_steward_ref is not None and not isinstance(self.data_steward_ref, RoleRegistryId):
            self.data_steward_ref = RoleRegistryId(self.data_steward_ref)

        if self.owning_unit_ref is not None and not isinstance(self.owning_unit_ref, OrganizationUnitRegistryId):
            self.owning_unit_ref = OrganizationUnitRegistryId(self.owning_unit_ref)

        if self.entity_type is not None and not isinstance(self.entity_type, EntityTypeEnum):
            self.entity_type = EntityTypeEnum(self.entity_type)

        if self.data_class is not None and not isinstance(self.data_class, DataClassEnum):
            self.data_class = DataClassEnum(self.data_class)

        if self.business_importance is not None and not isinstance(self.business_importance, BusinessImportanceEnum):
            self.business_importance = BusinessImportanceEnum(self.business_importance)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class LogicalEntity(ModelElement):
    """
    Представление бизнес-сущности в доменном контексте и модели конкретного решения.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["LogicalEntity"]
    class_class_curie: ClassVar[str] = "dams:LogicalEntity"
    class_name: ClassVar[str] = "LogicalEntity"
    class_model_uri: ClassVar[URIRef] = DAMS.LogicalEntity

    element_id: Union[str, LogicalEntityElementId] = None
    name: str = None
    description: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    context_ref: Union[str, DomainContextElementId] = None
    solution_data_role: Union[str, "SolutionDataRoleEnum"] = None
    conceptual_entity_refs: Optional[Union[Union[str, ConceptualEntityElementId], list[Union[str, ConceptualEntityElementId]]]] = empty_list()
    solution_ref: Optional[Union[str, ITSolutionRegistryId]] = None
    attributes: Optional[Union[dict[Union[str, LogicalAttributeElementId], Union[dict, "LogicalAttribute"]], list[Union[dict, "LogicalAttribute"]]]] = empty_dict()
    key_attribute_refs: Optional[Union[Union[str, URIorCURIE], list[Union[str, URIorCURIE]]]] = empty_list()
    invariant_refs: Optional[Union[Union[str, PolicyRegistryId], list[Union[str, PolicyRegistryId]]]] = empty_list()
    data_owner_ref: Optional[Union[str, RoleRegistryId]] = None
    data_steward_ref: Optional[Union[str, RoleRegistryId]] = None
    owning_unit_ref: Optional[Union[str, OrganizationUnitRegistryId]] = None
    entity_type: Optional[Union[str, "EntityTypeEnum"]] = None
    data_class: Optional[Union[str, "DataClassEnum"]] = None
    business_importance: Optional[Union[str, "BusinessImportanceEnum"]] = None
    governance_classification: Optional[Union[str, "GovernanceClassificationEnum"]] = None
    sensitivity_term_refs: Optional[Union[Union[str, DataClassificationTermRegistryId], list[Union[str, DataClassificationTermRegistryId]]]] = empty_list()
    classification_source: Optional[str] = None
    classification_rationale: Optional[str] = None
    policy_refs: Optional[Union[Union[str, PolicyRegistryId], list[Union[str, PolicyRegistryId]]]] = empty_list()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, LogicalEntityElementId):
            self.element_id = LogicalEntityElementId(self.element_id)

        if self._is_empty(self.context_ref):
            self.MissingRequiredField("context_ref")
        if not isinstance(self.context_ref, DomainContextElementId):
            self.context_ref = DomainContextElementId(self.context_ref)

        if self._is_empty(self.solution_data_role):
            self.MissingRequiredField("solution_data_role")
        if not isinstance(self.solution_data_role, SolutionDataRoleEnum):
            self.solution_data_role = SolutionDataRoleEnum(self.solution_data_role)

        if not isinstance(self.conceptual_entity_refs, list):
            self.conceptual_entity_refs = [self.conceptual_entity_refs] if self.conceptual_entity_refs is not None else []
        self.conceptual_entity_refs = [v if isinstance(v, ConceptualEntityElementId) else ConceptualEntityElementId(v) for v in self.conceptual_entity_refs]

        if self.solution_ref is not None and not isinstance(self.solution_ref, ITSolutionRegistryId):
            self.solution_ref = ITSolutionRegistryId(self.solution_ref)

        self._normalize_inlined_as_list(slot_name="attributes", slot_type=LogicalAttribute, key_name="element_id", keyed=True)

        if not isinstance(self.key_attribute_refs, list):
            self.key_attribute_refs = [self.key_attribute_refs] if self.key_attribute_refs is not None else []
        self.key_attribute_refs = [v if isinstance(v, URIorCURIE) else URIorCURIE(v) for v in self.key_attribute_refs]

        if not isinstance(self.invariant_refs, list):
            self.invariant_refs = [self.invariant_refs] if self.invariant_refs is not None else []
        self.invariant_refs = [v if isinstance(v, PolicyRegistryId) else PolicyRegistryId(v) for v in self.invariant_refs]

        if self.data_owner_ref is not None and not isinstance(self.data_owner_ref, RoleRegistryId):
            self.data_owner_ref = RoleRegistryId(self.data_owner_ref)

        if self.data_steward_ref is not None and not isinstance(self.data_steward_ref, RoleRegistryId):
            self.data_steward_ref = RoleRegistryId(self.data_steward_ref)

        if self.owning_unit_ref is not None and not isinstance(self.owning_unit_ref, OrganizationUnitRegistryId):
            self.owning_unit_ref = OrganizationUnitRegistryId(self.owning_unit_ref)

        if self.entity_type is not None and not isinstance(self.entity_type, EntityTypeEnum):
            self.entity_type = EntityTypeEnum(self.entity_type)

        if self.data_class is not None and not isinstance(self.data_class, DataClassEnum):
            self.data_class = DataClassEnum(self.data_class)

        if self.business_importance is not None and not isinstance(self.business_importance, BusinessImportanceEnum):
            self.business_importance = BusinessImportanceEnum(self.business_importance)

        if self.governance_classification is not None and not isinstance(self.governance_classification, GovernanceClassificationEnum):
            self.governance_classification = GovernanceClassificationEnum(self.governance_classification)

        if not isinstance(self.sensitivity_term_refs, list):
            self.sensitivity_term_refs = [self.sensitivity_term_refs] if self.sensitivity_term_refs is not None else []
        self.sensitivity_term_refs = [v if isinstance(v, DataClassificationTermRegistryId) else DataClassificationTermRegistryId(v) for v in self.sensitivity_term_refs]

        if self.classification_source is not None and not isinstance(self.classification_source, str):
            self.classification_source = str(self.classification_source)

        if self.classification_rationale is not None and not isinstance(self.classification_rationale, str):
            self.classification_rationale = str(self.classification_rationale)

        if not isinstance(self.policy_refs, list):
            self.policy_refs = [self.policy_refs] if self.policy_refs is not None else []
        self.policy_refs = [v if isinstance(v, PolicyRegistryId) else PolicyRegistryId(v) for v in self.policy_refs]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class LogicalAttribute(ModelElement):
    """
    Логический атрибут сущности с бизнес-смыслом, типом, обязательностью и классификацией.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["LogicalAttribute"]
    class_class_curie: ClassVar[str] = "dams:LogicalAttribute"
    class_name: ClassVar[str] = "LogicalAttribute"
    class_model_uri: ClassVar[URIRef] = DAMS.LogicalAttribute

    element_id: Union[str, LogicalAttributeElementId] = None
    name: str = None
    description: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    owner_entity_ref: Union[str, LogicalEntityElementId] = None
    logical_type: Union[str, "LogicalDataTypeEnum"] = None
    required: Union[bool, Bool] = None
    multivalued: Union[bool, Bool] = None
    minimum_cardinality: Optional[int] = None
    maximum_cardinality: Optional[int] = None
    value_set_ref: Optional[Union[str, URI]] = None
    format_pattern: Optional[str] = None
    default_value: Optional[str] = None
    derived_expression: Optional[str] = None
    governance_classification: Optional[Union[str, "GovernanceClassificationEnum"]] = None
    sensitivity_term_refs: Optional[Union[Union[str, DataClassificationTermRegistryId], list[Union[str, DataClassificationTermRegistryId]]]] = empty_list()
    classification_source: Optional[str] = None
    classification_rationale: Optional[str] = None
    policy_refs: Optional[Union[Union[str, PolicyRegistryId], list[Union[str, PolicyRegistryId]]]] = empty_list()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, LogicalAttributeElementId):
            self.element_id = LogicalAttributeElementId(self.element_id)

        if self._is_empty(self.owner_entity_ref):
            self.MissingRequiredField("owner_entity_ref")
        if not isinstance(self.owner_entity_ref, LogicalEntityElementId):
            self.owner_entity_ref = LogicalEntityElementId(self.owner_entity_ref)

        if self._is_empty(self.logical_type):
            self.MissingRequiredField("logical_type")
        if not isinstance(self.logical_type, LogicalDataTypeEnum):
            self.logical_type = LogicalDataTypeEnum(self.logical_type)

        if self._is_empty(self.required):
            self.MissingRequiredField("required")
        if not isinstance(self.required, Bool):
            self.required = Bool(self.required)

        if self._is_empty(self.multivalued):
            self.MissingRequiredField("multivalued")
        if not isinstance(self.multivalued, Bool):
            self.multivalued = Bool(self.multivalued)

        if self.minimum_cardinality is not None and not isinstance(self.minimum_cardinality, int):
            self.minimum_cardinality = int(self.minimum_cardinality)

        if self.maximum_cardinality is not None and not isinstance(self.maximum_cardinality, int):
            self.maximum_cardinality = int(self.maximum_cardinality)

        if self.value_set_ref is not None and not isinstance(self.value_set_ref, URI):
            self.value_set_ref = URI(self.value_set_ref)

        if self.format_pattern is not None and not isinstance(self.format_pattern, str):
            self.format_pattern = str(self.format_pattern)

        if self.default_value is not None and not isinstance(self.default_value, str):
            self.default_value = str(self.default_value)

        if self.derived_expression is not None and not isinstance(self.derived_expression, str):
            self.derived_expression = str(self.derived_expression)

        if self.governance_classification is not None and not isinstance(self.governance_classification, GovernanceClassificationEnum):
            self.governance_classification = GovernanceClassificationEnum(self.governance_classification)

        if not isinstance(self.sensitivity_term_refs, list):
            self.sensitivity_term_refs = [self.sensitivity_term_refs] if self.sensitivity_term_refs is not None else []
        self.sensitivity_term_refs = [v if isinstance(v, DataClassificationTermRegistryId) else DataClassificationTermRegistryId(v) for v in self.sensitivity_term_refs]

        if self.classification_source is not None and not isinstance(self.classification_source, str):
            self.classification_source = str(self.classification_source)

        if self.classification_rationale is not None and not isinstance(self.classification_rationale, str):
            self.classification_rationale = str(self.classification_rationale)

        if not isinstance(self.policy_refs, list):
            self.policy_refs = [self.policy_refs] if self.policy_refs is not None else []
        self.policy_refs = [v if isinstance(v, PolicyRegistryId) else PolicyRegistryId(v) for v in self.policy_refs]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Relationship(ModelElement):
    """
    Именованная связь между логическими или концептуальными сущностями.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["Relationship"]
    class_class_curie: ClassVar[str] = "dams:Relationship"
    class_name: ClassVar[str] = "Relationship"
    class_model_uri: ClassVar[URIRef] = DAMS.Relationship

    element_id: Union[str, RelationshipElementId] = None
    name: str = None
    description: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    source_entity_ref: Union[str, URIorCURIE] = None
    target_entity_ref: Union[str, URIorCURIE] = None
    source_role: Optional[str] = None
    target_role: Optional[str] = None
    source_min_cardinality: Optional[int] = None
    source_max_cardinality: Optional[int] = None
    target_min_cardinality: Optional[int] = None
    target_max_cardinality: Optional[int] = None
    identifying: Optional[Union[bool, Bool]] = None
    associative: Optional[Union[bool, Bool]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, RelationshipElementId):
            self.element_id = RelationshipElementId(self.element_id)

        if self._is_empty(self.source_entity_ref):
            self.MissingRequiredField("source_entity_ref")
        if not isinstance(self.source_entity_ref, URIorCURIE):
            self.source_entity_ref = URIorCURIE(self.source_entity_ref)

        if self._is_empty(self.target_entity_ref):
            self.MissingRequiredField("target_entity_ref")
        if not isinstance(self.target_entity_ref, URIorCURIE):
            self.target_entity_ref = URIorCURIE(self.target_entity_ref)

        if self.source_role is not None and not isinstance(self.source_role, str):
            self.source_role = str(self.source_role)

        if self.target_role is not None and not isinstance(self.target_role, str):
            self.target_role = str(self.target_role)

        if self.source_min_cardinality is not None and not isinstance(self.source_min_cardinality, int):
            self.source_min_cardinality = int(self.source_min_cardinality)

        if self.source_max_cardinality is not None and not isinstance(self.source_max_cardinality, int):
            self.source_max_cardinality = int(self.source_max_cardinality)

        if self.target_min_cardinality is not None and not isinstance(self.target_min_cardinality, int):
            self.target_min_cardinality = int(self.target_min_cardinality)

        if self.target_max_cardinality is not None and not isinstance(self.target_max_cardinality, int):
            self.target_max_cardinality = int(self.target_max_cardinality)

        if self.identifying is not None and not isinstance(self.identifying, Bool):
            self.identifying = Bool(self.identifying)

        if self.associative is not None and not isinstance(self.associative, Bool):
            self.associative = Bool(self.associative)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class PhysicalObject(ModelElement):
    """
    Квант данных или техническая точка публикации/потребления.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["PhysicalObject"]
    class_class_curie: ClassVar[str] = "dams:PhysicalObject"
    class_name: ClassVar[str] = "PhysicalObject"
    class_model_uri: ClassVar[URIRef] = DAMS.PhysicalObject

    element_id: Union[str, PhysicalObjectElementId] = None
    name: str = None
    description: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    system_ref: Union[str, ITSystemRegistryId] = None
    object_kind: Union[str, "PhysicalObjectKindEnum"] = None
    qualified_name: str = None
    technology: str = None
    native_schema_ref: Union[str, URI] = None
    direction: Union[str, "FlowDirectionEnum"] = None
    solution_ref: Optional[Union[str, ITSolutionRegistryId]] = None
    physical_fields: Optional[Union[dict[Union[str, PhysicalFieldElementId], Union[dict, "PhysicalField"]], list[Union[dict, "PhysicalField"]]]] = empty_dict()
    data_owner_ref: Optional[Union[str, RoleRegistryId]] = None
    data_steward_ref: Optional[Union[str, RoleRegistryId]] = None
    owning_unit_ref: Optional[Union[str, OrganizationUnitRegistryId]] = None
    policy_refs: Optional[Union[Union[str, PolicyRegistryId], list[Union[str, PolicyRegistryId]]]] = empty_list()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, PhysicalObjectElementId):
            self.element_id = PhysicalObjectElementId(self.element_id)

        if self._is_empty(self.system_ref):
            self.MissingRequiredField("system_ref")
        if not isinstance(self.system_ref, ITSystemRegistryId):
            self.system_ref = ITSystemRegistryId(self.system_ref)

        if self._is_empty(self.object_kind):
            self.MissingRequiredField("object_kind")
        if not isinstance(self.object_kind, PhysicalObjectKindEnum):
            self.object_kind = PhysicalObjectKindEnum(self.object_kind)

        if self._is_empty(self.qualified_name):
            self.MissingRequiredField("qualified_name")
        if not isinstance(self.qualified_name, str):
            self.qualified_name = str(self.qualified_name)

        if self._is_empty(self.technology):
            self.MissingRequiredField("technology")
        if not isinstance(self.technology, str):
            self.technology = str(self.technology)

        if self._is_empty(self.native_schema_ref):
            self.MissingRequiredField("native_schema_ref")
        if not isinstance(self.native_schema_ref, URI):
            self.native_schema_ref = URI(self.native_schema_ref)

        if self._is_empty(self.direction):
            self.MissingRequiredField("direction")
        if not isinstance(self.direction, FlowDirectionEnum):
            self.direction = FlowDirectionEnum(self.direction)

        if self.solution_ref is not None and not isinstance(self.solution_ref, ITSolutionRegistryId):
            self.solution_ref = ITSolutionRegistryId(self.solution_ref)

        self._normalize_inlined_as_list(slot_name="physical_fields", slot_type=PhysicalField, key_name="element_id", keyed=True)

        if self.data_owner_ref is not None and not isinstance(self.data_owner_ref, RoleRegistryId):
            self.data_owner_ref = RoleRegistryId(self.data_owner_ref)

        if self.data_steward_ref is not None and not isinstance(self.data_steward_ref, RoleRegistryId):
            self.data_steward_ref = RoleRegistryId(self.data_steward_ref)

        if self.owning_unit_ref is not None and not isinstance(self.owning_unit_ref, OrganizationUnitRegistryId):
            self.owning_unit_ref = OrganizationUnitRegistryId(self.owning_unit_ref)

        if not isinstance(self.policy_refs, list):
            self.policy_refs = [self.policy_refs] if self.policy_refs is not None else []
        self.policy_refs = [v if isinstance(v, PolicyRegistryId) else PolicyRegistryId(v) for v in self.policy_refs]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class PhysicalField(ModelElement):
    """
    Поле физического объекта; его семантика задаётся Mapping к LogicalAttribute.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["PhysicalField"]
    class_class_curie: ClassVar[str] = "dams:PhysicalField"
    class_name: ClassVar[str] = "PhysicalField"
    class_model_uri: ClassVar[URIRef] = DAMS.PhysicalField

    element_id: Union[str, PhysicalFieldElementId] = None
    name: str = None
    description: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    physical_object_ref: Union[str, PhysicalObjectElementId] = None
    native_name: str = None
    native_type: str = None
    required: Union[bool, Bool] = None
    ordinal_position: Optional[int] = None
    schema_path: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, PhysicalFieldElementId):
            self.element_id = PhysicalFieldElementId(self.element_id)

        if self._is_empty(self.physical_object_ref):
            self.MissingRequiredField("physical_object_ref")
        if not isinstance(self.physical_object_ref, PhysicalObjectElementId):
            self.physical_object_ref = PhysicalObjectElementId(self.physical_object_ref)

        if self._is_empty(self.native_name):
            self.MissingRequiredField("native_name")
        if not isinstance(self.native_name, str):
            self.native_name = str(self.native_name)

        if self._is_empty(self.native_type):
            self.MissingRequiredField("native_type")
        if not isinstance(self.native_type, str):
            self.native_type = str(self.native_type)

        if self._is_empty(self.required):
            self.MissingRequiredField("required")
        if not isinstance(self.required, Bool):
            self.required = Bool(self.required)

        if self.ordinal_position is not None and not isinstance(self.ordinal_position, int):
            self.ordinal_position = int(self.ordinal_position)

        if self.schema_path is not None and not isinstance(self.schema_path, str):
            self.schema_path = str(self.schema_path)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Mapping(ModelElement):
    """
    Явное соответствие между элементами. Discriminate via mapping_type: realizes (solution→enterprise conceptual),
    field_mapping/mapsTo (physical↔logical), aligns_with (enterprise↔external term). Not used for SpecImpl
    implements/conforms_to.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["Mapping"]
    class_class_curie: ClassVar[str] = "dams:Mapping"
    class_name: ClassVar[str] = "Mapping"
    class_model_uri: ClassVar[URIRef] = DAMS.Mapping

    element_id: Union[str, MappingElementId] = None
    name: str = None
    description: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    mapping_type: Union[str, "MappingTypeEnum"] = None
    mapping_cardinality: Union[str, "MappingCardinalityEnum"] = None
    source_refs: Optional[Union[Union[str, URIorCURIE], list[Union[str, URIorCURIE]]]] = empty_list()
    target_refs: Optional[Union[Union[str, URIorCURIE], list[Union[str, URIorCURIE]]]] = empty_list()
    transformation_ref: Optional[Union[str, URI]] = None
    transformation_expression: Optional[str] = None
    confidence: Optional[Decimal] = None
    valid_from: Optional[Union[str, XSDDateTime]] = None
    valid_to: Optional[Union[str, XSDDateTime]] = None
    source_artifact_ref: Optional[Union[str, URI]] = None
    evidence_refs: Optional[Union[Union[str, URI], list[Union[str, URI]]]] = empty_list()
    approval_status: Optional[Union[str, "ApprovalStatusEnum"]] = None
    approved_by_ref: Optional[Union[str, RoleRegistryId]] = None
    approved_at: Optional[Union[str, XSDDateTime]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, MappingElementId):
            self.element_id = MappingElementId(self.element_id)

        if self._is_empty(self.mapping_type):
            self.MissingRequiredField("mapping_type")
        if not isinstance(self.mapping_type, MappingTypeEnum):
            self.mapping_type = MappingTypeEnum(self.mapping_type)

        if self._is_empty(self.mapping_cardinality):
            self.MissingRequiredField("mapping_cardinality")
        if not isinstance(self.mapping_cardinality, MappingCardinalityEnum):
            self.mapping_cardinality = MappingCardinalityEnum(self.mapping_cardinality)

        if not isinstance(self.source_refs, list):
            self.source_refs = [self.source_refs] if self.source_refs is not None else []
        self.source_refs = [v if isinstance(v, URIorCURIE) else URIorCURIE(v) for v in self.source_refs]

        if not isinstance(self.target_refs, list):
            self.target_refs = [self.target_refs] if self.target_refs is not None else []
        self.target_refs = [v if isinstance(v, URIorCURIE) else URIorCURIE(v) for v in self.target_refs]

        if self.transformation_ref is not None and not isinstance(self.transformation_ref, URI):
            self.transformation_ref = URI(self.transformation_ref)

        if self.transformation_expression is not None and not isinstance(self.transformation_expression, str):
            self.transformation_expression = str(self.transformation_expression)

        if self.confidence is not None and not isinstance(self.confidence, Decimal):
            self.confidence = Decimal(self.confidence)

        if self.valid_from is not None and not isinstance(self.valid_from, XSDDateTime):
            self.valid_from = XSDDateTime(self.valid_from)

        if self.valid_to is not None and not isinstance(self.valid_to, XSDDateTime):
            self.valid_to = XSDDateTime(self.valid_to)

        if self.source_artifact_ref is not None and not isinstance(self.source_artifact_ref, URI):
            self.source_artifact_ref = URI(self.source_artifact_ref)

        if not isinstance(self.evidence_refs, list):
            self.evidence_refs = [self.evidence_refs] if self.evidence_refs is not None else []
        self.evidence_refs = [v if isinstance(v, URI) else URI(v) for v in self.evidence_refs]

        if self.approval_status is not None and not isinstance(self.approval_status, ApprovalStatusEnum):
            self.approval_status = ApprovalStatusEnum(self.approval_status)

        if self.approved_by_ref is not None and not isinstance(self.approved_by_ref, RoleRegistryId):
            self.approved_by_ref = RoleRegistryId(self.approved_by_ref)

        if self.approved_at is not None and not isinstance(self.approved_at, XSDDateTime):
            self.approved_at = XSDDateTime(self.approved_at)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class DataFlow(ModelElement):
    """
    Ссылочная проекция зарегистрированной интеграции; топология и канал являются данными Clinkr, а семантика — модели
    данных.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["DataFlow"]
    class_class_curie: ClassVar[str] = "dams:DataFlow"
    class_name: ClassVar[str] = "DataFlow"
    class_model_uri: ClassVar[URIRef] = DAMS.DataFlow

    element_id: Union[str, DataFlowElementId] = None
    name: str = None
    description: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    integration_ref: Union[str, IntegrationReferenceRegistryId] = None
    source_solution_ref: Union[str, ITSolutionRegistryId] = None
    target_solution_ref: Union[str, ITSolutionRegistryId] = None
    source_system_ref: Union[str, ITSystemRegistryId] = None
    target_system_ref: Union[str, ITSystemRegistryId] = None
    source_platform_ref: Union[str, ITPlatformRegistryId] = None
    target_platform_ref: Union[str, ITPlatformRegistryId] = None
    integration_level: Union[str, "IntegrationLevelEnum"] = None
    integration_class: Union[str, "IntegrationClassEnum"] = None
    integration_channel: Union[str, "IntegrationChannelEnum"] = None
    integration_spec_ref: Union[str, URI] = None
    valid_from: Optional[Union[str, XSDDateTime]] = None
    valid_to: Optional[Union[str, XSDDateTime]] = None
    deprecated_by_ref: Optional[Union[str, URIorCURIE]] = None
    contract_ref: Optional[Union[str, DataContractReferenceRegistryId]] = None
    entity_bindings: Optional[Union[dict[Union[str, DataFlowEntityBindingElementId], Union[dict, "DataFlowEntityBinding"]], list[Union[dict, "DataFlowEntityBinding"]]]] = empty_dict()
    data_owner_ref: Optional[Union[str, RoleRegistryId]] = None
    data_steward_ref: Optional[Union[str, RoleRegistryId]] = None
    owning_unit_ref: Optional[Union[str, OrganizationUnitRegistryId]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, DataFlowElementId):
            self.element_id = DataFlowElementId(self.element_id)

        if self._is_empty(self.lifecycle_status):
            self.MissingRequiredField("lifecycle_status")
        if not isinstance(self.lifecycle_status, LifecycleStatusEnum):
            self.lifecycle_status = LifecycleStatusEnum(self.lifecycle_status)

        if self._is_empty(self.integration_ref):
            self.MissingRequiredField("integration_ref")
        if not isinstance(self.integration_ref, IntegrationReferenceRegistryId):
            self.integration_ref = IntegrationReferenceRegistryId(self.integration_ref)

        if self._is_empty(self.source_solution_ref):
            self.MissingRequiredField("source_solution_ref")
        if not isinstance(self.source_solution_ref, ITSolutionRegistryId):
            self.source_solution_ref = ITSolutionRegistryId(self.source_solution_ref)

        if self._is_empty(self.target_solution_ref):
            self.MissingRequiredField("target_solution_ref")
        if not isinstance(self.target_solution_ref, ITSolutionRegistryId):
            self.target_solution_ref = ITSolutionRegistryId(self.target_solution_ref)

        if self._is_empty(self.source_system_ref):
            self.MissingRequiredField("source_system_ref")
        if not isinstance(self.source_system_ref, ITSystemRegistryId):
            self.source_system_ref = ITSystemRegistryId(self.source_system_ref)

        if self._is_empty(self.target_system_ref):
            self.MissingRequiredField("target_system_ref")
        if not isinstance(self.target_system_ref, ITSystemRegistryId):
            self.target_system_ref = ITSystemRegistryId(self.target_system_ref)

        if self._is_empty(self.source_platform_ref):
            self.MissingRequiredField("source_platform_ref")
        if not isinstance(self.source_platform_ref, ITPlatformRegistryId):
            self.source_platform_ref = ITPlatformRegistryId(self.source_platform_ref)

        if self._is_empty(self.target_platform_ref):
            self.MissingRequiredField("target_platform_ref")
        if not isinstance(self.target_platform_ref, ITPlatformRegistryId):
            self.target_platform_ref = ITPlatformRegistryId(self.target_platform_ref)

        if self._is_empty(self.integration_level):
            self.MissingRequiredField("integration_level")
        if not isinstance(self.integration_level, IntegrationLevelEnum):
            self.integration_level = IntegrationLevelEnum(self.integration_level)

        if self._is_empty(self.integration_class):
            self.MissingRequiredField("integration_class")
        if not isinstance(self.integration_class, IntegrationClassEnum):
            self.integration_class = IntegrationClassEnum(self.integration_class)

        if self._is_empty(self.integration_channel):
            self.MissingRequiredField("integration_channel")
        if not isinstance(self.integration_channel, IntegrationChannelEnum):
            self.integration_channel = IntegrationChannelEnum(self.integration_channel)

        if self._is_empty(self.integration_spec_ref):
            self.MissingRequiredField("integration_spec_ref")
        if not isinstance(self.integration_spec_ref, URI):
            self.integration_spec_ref = URI(self.integration_spec_ref)

        if self.valid_from is not None and not isinstance(self.valid_from, XSDDateTime):
            self.valid_from = XSDDateTime(self.valid_from)

        if self.valid_to is not None and not isinstance(self.valid_to, XSDDateTime):
            self.valid_to = XSDDateTime(self.valid_to)

        if self.deprecated_by_ref is not None and not isinstance(self.deprecated_by_ref, URIorCURIE):
            self.deprecated_by_ref = URIorCURIE(self.deprecated_by_ref)

        if self.contract_ref is not None and not isinstance(self.contract_ref, DataContractReferenceRegistryId):
            self.contract_ref = DataContractReferenceRegistryId(self.contract_ref)

        self._normalize_inlined_as_list(slot_name="entity_bindings", slot_type=DataFlowEntityBinding, key_name="element_id", keyed=True)

        if self.data_owner_ref is not None and not isinstance(self.data_owner_ref, RoleRegistryId):
            self.data_owner_ref = RoleRegistryId(self.data_owner_ref)

        if self.data_steward_ref is not None and not isinstance(self.data_steward_ref, RoleRegistryId):
            self.data_steward_ref = RoleRegistryId(self.data_steward_ref)

        if self.owning_unit_ref is not None and not isinstance(self.owning_unit_ref, OrganizationUnitRegistryId):
            self.owning_unit_ref = OrganizationUnitRegistryId(self.owning_unit_ref)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class DataFlowEntityBinding(ModelElement):
    """
    Связь потока с логическими сущностями, атрибутами и физическими объектами модели решения.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["DataFlowEntityBinding"]
    class_class_curie: ClassVar[str] = "dams:DataFlowEntityBinding"
    class_name: ClassVar[str] = "DataFlowEntityBinding"
    class_model_uri: ClassVar[URIRef] = DAMS.DataFlowEntityBinding

    element_id: Union[str, DataFlowEntityBindingElementId] = None
    name: str = None
    description: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    flow_ref: Union[str, DataFlowElementId] = None
    source_model_ref: Union[str, URI] = None
    logical_entity_ref: Union[str, LogicalEntityElementId] = None
    direction: Union[str, "FlowDirectionEnum"] = None
    logical_attribute_refs: Optional[Union[Union[str, LogicalAttributeElementId], list[Union[str, LogicalAttributeElementId]]]] = empty_list()
    physical_object_refs: Optional[Union[Union[str, PhysicalObjectElementId], list[Union[str, PhysicalObjectElementId]]]] = empty_list()
    physical_field_refs: Optional[Union[Union[str, PhysicalFieldElementId], list[Union[str, PhysicalFieldElementId]]]] = empty_list()
    transformation_mapping_refs: Optional[Union[Union[str, MappingElementId], list[Union[str, MappingElementId]]]] = empty_list()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, DataFlowEntityBindingElementId):
            self.element_id = DataFlowEntityBindingElementId(self.element_id)

        if self._is_empty(self.flow_ref):
            self.MissingRequiredField("flow_ref")
        if not isinstance(self.flow_ref, DataFlowElementId):
            self.flow_ref = DataFlowElementId(self.flow_ref)

        if self._is_empty(self.source_model_ref):
            self.MissingRequiredField("source_model_ref")
        if not isinstance(self.source_model_ref, URI):
            self.source_model_ref = URI(self.source_model_ref)

        if self._is_empty(self.logical_entity_ref):
            self.MissingRequiredField("logical_entity_ref")
        if not isinstance(self.logical_entity_ref, LogicalEntityElementId):
            self.logical_entity_ref = LogicalEntityElementId(self.logical_entity_ref)

        if self._is_empty(self.direction):
            self.MissingRequiredField("direction")
        if not isinstance(self.direction, FlowDirectionEnum):
            self.direction = FlowDirectionEnum(self.direction)

        if not isinstance(self.logical_attribute_refs, list):
            self.logical_attribute_refs = [self.logical_attribute_refs] if self.logical_attribute_refs is not None else []
        self.logical_attribute_refs = [v if isinstance(v, LogicalAttributeElementId) else LogicalAttributeElementId(v) for v in self.logical_attribute_refs]

        if not isinstance(self.physical_object_refs, list):
            self.physical_object_refs = [self.physical_object_refs] if self.physical_object_refs is not None else []
        self.physical_object_refs = [v if isinstance(v, PhysicalObjectElementId) else PhysicalObjectElementId(v) for v in self.physical_object_refs]

        if not isinstance(self.physical_field_refs, list):
            self.physical_field_refs = [self.physical_field_refs] if self.physical_field_refs is not None else []
        self.physical_field_refs = [v if isinstance(v, PhysicalFieldElementId) else PhysicalFieldElementId(v) for v in self.physical_field_refs]

        if not isinstance(self.transformation_mapping_refs, list):
            self.transformation_mapping_refs = [self.transformation_mapping_refs] if self.transformation_mapping_refs is not None else []
        self.transformation_mapping_refs = [v if isinstance(v, MappingElementId) else MappingElementId(v) for v in self.transformation_mapping_refs]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class DataModelBinding(ModelElement):
    """
    Дочерняя модельная спецификация дата-контракта, фиксирующая неизменяемую ревизию модели и передаваемый срез.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["DataModelBinding"]
    class_class_curie: ClassVar[str] = "dams:DataModelBinding"
    class_name: ClassVar[str] = "DataModelBinding"
    class_model_uri: ClassVar[URIRef] = DAMS.DataModelBinding

    element_id: Union[str, DataModelBindingElementId] = None
    name: str = None
    description: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    specification_version: Union[str, SemVer] = None
    implementation_version: Union[str, SemVer] = None
    integration_ref: Union[str, IntegrationReferenceRegistryId] = None
    model_package_ref: Union[str, URI] = None
    model_version: Union[str, SemVer] = None
    model_revision: str = None
    compatibility_mode: Union[str, "CompatibilityModeEnum"] = None
    integrity_digest: Union[str, Sha256Digest] = None
    generated_at: Union[str, XSDDateTime] = None
    valid_from: Optional[Union[str, XSDDateTime]] = None
    valid_to: Optional[Union[str, XSDDateTime]] = None
    deprecated_by_ref: Optional[Union[str, URIorCURIE]] = None
    contract_ref: Optional[Union[str, DataContractReferenceRegistryId]] = None
    selections: Optional[Union[dict[Union[str, ModelSelectionElementId], Union[dict, "ModelSelection"]], list[Union[dict, "ModelSelection"]]]] = empty_dict()
    compatibility_baseline_ref: Optional[Union[str, URI]] = None
    data_owner_ref: Optional[Union[str, RoleRegistryId]] = None
    data_steward_ref: Optional[Union[str, RoleRegistryId]] = None
    owning_unit_ref: Optional[Union[str, OrganizationUnitRegistryId]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, DataModelBindingElementId):
            self.element_id = DataModelBindingElementId(self.element_id)

        if self._is_empty(self.lifecycle_status):
            self.MissingRequiredField("lifecycle_status")
        if not isinstance(self.lifecycle_status, LifecycleStatusEnum):
            self.lifecycle_status = LifecycleStatusEnum(self.lifecycle_status)

        if self._is_empty(self.specification_version):
            self.MissingRequiredField("specification_version")
        if not isinstance(self.specification_version, SemVer):
            self.specification_version = SemVer(self.specification_version)

        if self._is_empty(self.implementation_version):
            self.MissingRequiredField("implementation_version")
        if not isinstance(self.implementation_version, SemVer):
            self.implementation_version = SemVer(self.implementation_version)

        if self._is_empty(self.integration_ref):
            self.MissingRequiredField("integration_ref")
        if not isinstance(self.integration_ref, IntegrationReferenceRegistryId):
            self.integration_ref = IntegrationReferenceRegistryId(self.integration_ref)

        if self._is_empty(self.model_package_ref):
            self.MissingRequiredField("model_package_ref")
        if not isinstance(self.model_package_ref, URI):
            self.model_package_ref = URI(self.model_package_ref)

        if self._is_empty(self.model_version):
            self.MissingRequiredField("model_version")
        if not isinstance(self.model_version, SemVer):
            self.model_version = SemVer(self.model_version)

        if self._is_empty(self.model_revision):
            self.MissingRequiredField("model_revision")
        if not isinstance(self.model_revision, str):
            self.model_revision = str(self.model_revision)

        if self._is_empty(self.compatibility_mode):
            self.MissingRequiredField("compatibility_mode")
        if not isinstance(self.compatibility_mode, CompatibilityModeEnum):
            self.compatibility_mode = CompatibilityModeEnum(self.compatibility_mode)

        if self._is_empty(self.integrity_digest):
            self.MissingRequiredField("integrity_digest")
        if not isinstance(self.integrity_digest, Sha256Digest):
            self.integrity_digest = Sha256Digest(self.integrity_digest)

        if self._is_empty(self.generated_at):
            self.MissingRequiredField("generated_at")
        if not isinstance(self.generated_at, XSDDateTime):
            self.generated_at = XSDDateTime(self.generated_at)

        if self.valid_from is not None and not isinstance(self.valid_from, XSDDateTime):
            self.valid_from = XSDDateTime(self.valid_from)

        if self.valid_to is not None and not isinstance(self.valid_to, XSDDateTime):
            self.valid_to = XSDDateTime(self.valid_to)

        if self.deprecated_by_ref is not None and not isinstance(self.deprecated_by_ref, URIorCURIE):
            self.deprecated_by_ref = URIorCURIE(self.deprecated_by_ref)

        if self.contract_ref is not None and not isinstance(self.contract_ref, DataContractReferenceRegistryId):
            self.contract_ref = DataContractReferenceRegistryId(self.contract_ref)

        self._normalize_inlined_as_list(slot_name="selections", slot_type=ModelSelection, key_name="element_id", keyed=True)

        if self.compatibility_baseline_ref is not None and not isinstance(self.compatibility_baseline_ref, URI):
            self.compatibility_baseline_ref = URI(self.compatibility_baseline_ref)

        if self.data_owner_ref is not None and not isinstance(self.data_owner_ref, RoleRegistryId):
            self.data_owner_ref = RoleRegistryId(self.data_owner_ref)

        if self.data_steward_ref is not None and not isinstance(self.data_steward_ref, RoleRegistryId):
            self.data_steward_ref = RoleRegistryId(self.data_steward_ref)

        if self.owning_unit_ref is not None and not isinstance(self.owning_unit_ref, OrganizationUnitRegistryId):
            self.owning_unit_ref = OrganizationUnitRegistryId(self.owning_unit_ref)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ModelSelection(ModelElement):
    """
    Переиспользуемый набор выбранных сущностей, атрибутов и физических представлений.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["ModelSelection"]
    class_class_curie: ClassVar[str] = "dams:ModelSelection"
    class_name: ClassVar[str] = "ModelSelection"
    class_model_uri: ClassVar[URIRef] = DAMS.ModelSelection

    element_id: Union[str, ModelSelectionElementId] = None
    name: str = None
    description: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    selected_entities: Optional[Union[dict[Union[str, SelectedEntityElementId], Union[dict, "SelectedEntity"]], list[Union[dict, "SelectedEntity"]]]] = empty_dict()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, ModelSelectionElementId):
            self.element_id = ModelSelectionElementId(self.element_id)

        self._normalize_inlined_as_list(slot_name="selected_entities", slot_type=SelectedEntity, key_name="element_id", keyed=True)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class SelectedEntity(ModelElement):
    """
    Выбранная для интеграции логическая сущность.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["SelectedEntity"]
    class_class_curie: ClassVar[str] = "dams:SelectedEntity"
    class_name: ClassVar[str] = "SelectedEntity"
    class_model_uri: ClassVar[URIRef] = DAMS.SelectedEntity

    element_id: Union[str, SelectedEntityElementId] = None
    name: str = None
    description: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    logical_entity_ref: Union[str, LogicalEntityElementId] = None
    selected_attributes: Optional[Union[dict[Union[str, SelectedAttributeElementId], Union[dict, "SelectedAttribute"]], list[Union[dict, "SelectedAttribute"]]]] = empty_dict()
    physical_object_refs: Optional[Union[Union[str, PhysicalObjectElementId], list[Union[str, PhysicalObjectElementId]]]] = empty_list()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, SelectedEntityElementId):
            self.element_id = SelectedEntityElementId(self.element_id)

        if self._is_empty(self.logical_entity_ref):
            self.MissingRequiredField("logical_entity_ref")
        if not isinstance(self.logical_entity_ref, LogicalEntityElementId):
            self.logical_entity_ref = LogicalEntityElementId(self.logical_entity_ref)

        self._normalize_inlined_as_list(slot_name="selected_attributes", slot_type=SelectedAttribute, key_name="element_id", keyed=True)

        if not isinstance(self.physical_object_refs, list):
            self.physical_object_refs = [self.physical_object_refs] if self.physical_object_refs is not None else []
        self.physical_object_refs = [v if isinstance(v, PhysicalObjectElementId) else PhysicalObjectElementId(v) for v in self.physical_object_refs]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class SelectedAttribute(ModelElement):
    """
    Выбранный атрибут и соответствующее физическое поле payload, таблицы или сообщения.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["SelectedAttribute"]
    class_class_curie: ClassVar[str] = "dams:SelectedAttribute"
    class_name: ClassVar[str] = "SelectedAttribute"
    class_model_uri: ClassVar[URIRef] = DAMS.SelectedAttribute

    element_id: Union[str, SelectedAttributeElementId] = None
    name: str = None
    description: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    logical_attribute_ref: Union[str, LogicalAttributeElementId] = None
    physical_field_refs: Optional[Union[Union[str, PhysicalFieldElementId], list[Union[str, PhysicalFieldElementId]]]] = empty_list()
    transformation_mapping_ref: Optional[Union[str, MappingElementId]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, SelectedAttributeElementId):
            self.element_id = SelectedAttributeElementId(self.element_id)

        if self._is_empty(self.logical_attribute_ref):
            self.MissingRequiredField("logical_attribute_ref")
        if not isinstance(self.logical_attribute_ref, LogicalAttributeElementId):
            self.logical_attribute_ref = LogicalAttributeElementId(self.logical_attribute_ref)

        if not isinstance(self.physical_field_refs, list):
            self.physical_field_refs = [self.physical_field_refs] if self.physical_field_refs is not None else []
        self.physical_field_refs = [v if isinstance(v, PhysicalFieldElementId) else PhysicalFieldElementId(v) for v in self.physical_field_refs]

        if self.transformation_mapping_ref is not None and not isinstance(self.transformation_mapping_ref, MappingElementId):
            self.transformation_mapping_ref = MappingElementId(self.transformation_mapping_ref)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Metric(ModelElement):
    """
    Управляемое определение бизнес- или технической метрики; является опциональным аналитическим профилем.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["Metric"]
    class_class_curie: ClassVar[str] = "dams:Metric"
    class_name: ClassVar[str] = "Metric"
    class_model_uri: ClassVar[URIRef] = DAMS.Metric

    element_id: Union[str, MetricElementId] = None
    name: str = None
    description: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    metric_expression: str = None
    aggregation_function: str = None
    grain_entity_refs: Optional[Union[Union[str, LogicalEntityElementId], list[Union[str, LogicalEntityElementId]]]] = empty_list()
    dimension_attribute_refs: Optional[Union[Union[str, LogicalAttributeElementId], list[Union[str, LogicalAttributeElementId]]]] = empty_list()
    measure_attribute_refs: Optional[Union[Union[str, LogicalAttributeElementId], list[Union[str, LogicalAttributeElementId]]]] = empty_list()
    unit: Optional[str] = None
    filter_expression: Optional[str] = None
    data_owner_ref: Optional[Union[str, RoleRegistryId]] = None
    data_steward_ref: Optional[Union[str, RoleRegistryId]] = None
    owning_unit_ref: Optional[Union[str, OrganizationUnitRegistryId]] = None
    policy_refs: Optional[Union[Union[str, PolicyRegistryId], list[Union[str, PolicyRegistryId]]]] = empty_list()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, MetricElementId):
            self.element_id = MetricElementId(self.element_id)

        if self._is_empty(self.metric_expression):
            self.MissingRequiredField("metric_expression")
        if not isinstance(self.metric_expression, str):
            self.metric_expression = str(self.metric_expression)

        if self._is_empty(self.aggregation_function):
            self.MissingRequiredField("aggregation_function")
        if not isinstance(self.aggregation_function, str):
            self.aggregation_function = str(self.aggregation_function)

        if not isinstance(self.grain_entity_refs, list):
            self.grain_entity_refs = [self.grain_entity_refs] if self.grain_entity_refs is not None else []
        self.grain_entity_refs = [v if isinstance(v, LogicalEntityElementId) else LogicalEntityElementId(v) for v in self.grain_entity_refs]

        if not isinstance(self.dimension_attribute_refs, list):
            self.dimension_attribute_refs = [self.dimension_attribute_refs] if self.dimension_attribute_refs is not None else []
        self.dimension_attribute_refs = [v if isinstance(v, LogicalAttributeElementId) else LogicalAttributeElementId(v) for v in self.dimension_attribute_refs]

        if not isinstance(self.measure_attribute_refs, list):
            self.measure_attribute_refs = [self.measure_attribute_refs] if self.measure_attribute_refs is not None else []
        self.measure_attribute_refs = [v if isinstance(v, LogicalAttributeElementId) else LogicalAttributeElementId(v) for v in self.measure_attribute_refs]

        if self.unit is not None and not isinstance(self.unit, str):
            self.unit = str(self.unit)

        if self.filter_expression is not None and not isinstance(self.filter_expression, str):
            self.filter_expression = str(self.filter_expression)

        if self.data_owner_ref is not None and not isinstance(self.data_owner_ref, RoleRegistryId):
            self.data_owner_ref = RoleRegistryId(self.data_owner_ref)

        if self.data_steward_ref is not None and not isinstance(self.data_steward_ref, RoleRegistryId):
            self.data_steward_ref = RoleRegistryId(self.data_steward_ref)

        if self.owning_unit_ref is not None and not isinstance(self.owning_unit_ref, OrganizationUnitRegistryId):
            self.owning_unit_ref = OrganizationUnitRegistryId(self.owning_unit_ref)

        if not isinstance(self.policy_refs, list):
            self.policy_refs = [self.policy_refs] if self.policy_refs is not None else []
        self.policy_refs = [v if isinstance(v, PolicyRegistryId) else PolicyRegistryId(v) for v in self.policy_refs]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Dimension(ModelElement):
    """
    Переиспользуемое аналитическое измерение, связанное с логическими атрибутами.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["Dimension"]
    class_class_curie: ClassVar[str] = "dams:Dimension"
    class_name: ClassVar[str] = "Dimension"
    class_model_uri: ClassVar[URIRef] = DAMS.Dimension

    element_id: Union[str, DimensionElementId] = None
    name: str = None
    description: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    dimension_attribute_refs: Optional[Union[Union[str, LogicalAttributeElementId], list[Union[str, LogicalAttributeElementId]]]] = empty_list()
    grain_entity_refs: Optional[Union[Union[str, LogicalEntityElementId], list[Union[str, LogicalEntityElementId]]]] = empty_list()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, DimensionElementId):
            self.element_id = DimensionElementId(self.element_id)

        if not isinstance(self.dimension_attribute_refs, list):
            self.dimension_attribute_refs = [self.dimension_attribute_refs] if self.dimension_attribute_refs is not None else []
        self.dimension_attribute_refs = [v if isinstance(v, LogicalAttributeElementId) else LogicalAttributeElementId(v) for v in self.dimension_attribute_refs]

        if not isinstance(self.grain_entity_refs, list):
            self.grain_entity_refs = [self.grain_entity_refs] if self.grain_entity_refs is not None else []
        self.grain_entity_refs = [v if isinstance(v, LogicalEntityElementId) else LogicalEntityElementId(v) for v in self.grain_entity_refs]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class FormalCheck(YAMLRoot):
    """
    Одна машиночитаемая проверка требования. Kind выровнен с LinkML constraints и DAMS reference/structural
    diagnostics; assess wiring может появиться позже.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["FormalCheck"]
    class_class_curie: ClassVar[str] = "dams:FormalCheck"
    class_name: ClassVar[str] = "FormalCheck"
    class_model_uri: ClassVar[URIRef] = DAMS.FormalCheck

    check_id: Union[str, FormalCheckCheckId] = None
    kind: Union[str, "FormalCheckKindEnum"] = None
    severity: Union[str, "CheckSeverityEnum"] = None
    target_class: Optional[str] = None
    target_slot: Optional[str] = None
    target_path: Optional[str] = None
    diagnostic_code: Optional[str] = None
    expression: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.check_id):
            self.MissingRequiredField("check_id")
        if not isinstance(self.check_id, FormalCheckCheckId):
            self.check_id = FormalCheckCheckId(self.check_id)

        if self._is_empty(self.kind):
            self.MissingRequiredField("kind")
        if not isinstance(self.kind, FormalCheckKindEnum):
            self.kind = FormalCheckKindEnum(self.kind)

        if self._is_empty(self.severity):
            self.MissingRequiredField("severity")
        if not isinstance(self.severity, CheckSeverityEnum):
            self.severity = CheckSeverityEnum(self.severity)

        if self.target_class is not None and not isinstance(self.target_class, str):
            self.target_class = str(self.target_class)

        if self.target_slot is not None and not isinstance(self.target_slot, str):
            self.target_slot = str(self.target_slot)

        if self.target_path is not None and not isinstance(self.target_path, str):
            self.target_path = str(self.target_path)

        if self.diagnostic_code is not None and not isinstance(self.diagnostic_code, str):
            self.diagnostic_code = str(self.diagnostic_code)

        if self.expression is not None and not isinstance(self.expression, str):
            self.expression = str(self.expression)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class SpecificationRequirement(ModelElement):
    """
    Нормативное требование к модели, соответствующей reference specification (каталог для уровня ИТ-решения и др.).
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["SpecificationRequirement"]
    class_class_curie: ClassVar[str] = "dams:SpecificationRequirement"
    class_name: ClassVar[str] = "SpecificationRequirement"
    class_model_uri: ClassVar[URIRef] = DAMS.SpecificationRequirement

    element_id: Union[str, SpecificationRequirementElementId] = None
    name: str = None
    description: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    code: str = None
    requirement_level: Union[str, "RequirementLevelEnum"] = None
    requirement_section: Union[str, "RequirementSectionEnum"] = None
    statement: str = None
    formal_checks: Optional[Union[dict[Union[str, FormalCheckCheckId], Union[dict, FormalCheck]], list[Union[dict, FormalCheck]]]] = empty_dict()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, SpecificationRequirementElementId):
            self.element_id = SpecificationRequirementElementId(self.element_id)

        if self._is_empty(self.code):
            self.MissingRequiredField("code")
        if not isinstance(self.code, str):
            self.code = str(self.code)

        if self._is_empty(self.requirement_level):
            self.MissingRequiredField("requirement_level")
        if not isinstance(self.requirement_level, RequirementLevelEnum):
            self.requirement_level = RequirementLevelEnum(self.requirement_level)

        if self._is_empty(self.requirement_section):
            self.MissingRequiredField("requirement_section")
        if not isinstance(self.requirement_section, RequirementSectionEnum):
            self.requirement_section = RequirementSectionEnum(self.requirement_section)

        if self._is_empty(self.statement):
            self.MissingRequiredField("statement")
        if not isinstance(self.statement, str):
            self.statement = str(self.statement)

        self._normalize_inlined_as_list(slot_name="formal_checks", slot_type=FormalCheck, key_name="check_id", keyed=True)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class RequirementCatalog(YAMLRoot):
    """
    Контейнер инстансов SpecificationRequirement вне ModelPackage.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["RequirementCatalog"]
    class_class_curie: ClassVar[str] = "dams:RequirementCatalog"
    class_name: ClassVar[str] = "RequirementCatalog"
    class_model_uri: ClassVar[URIRef] = DAMS.RequirementCatalog

    catalog_id: Union[str, RequirementCatalogCatalogId] = None
    name: str = None
    requirements: Optional[Union[dict[Union[str, SpecificationRequirementElementId], Union[dict, SpecificationRequirement]], list[Union[dict, SpecificationRequirement]]]] = empty_dict()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.catalog_id):
            self.MissingRequiredField("catalog_id")
        if not isinstance(self.catalog_id, RequirementCatalogCatalogId):
            self.catalog_id = RequirementCatalogCatalogId(self.catalog_id)

        if self._is_empty(self.name):
            self.MissingRequiredField("name")
        if not isinstance(self.name, str):
            self.name = str(self.name)

        self._normalize_inlined_as_list(slot_name="requirements", slot_type=SpecificationRequirement, key_name="element_id", keyed=True)

        super().__post_init__(**kwargs)


# Enumerations
class LifecycleStatusEnum(EnumDefinitionImpl):

    draft = PermissibleValue(text="draft")
    active = PermissibleValue(text="active")
    deprecated = PermissibleValue(text="deprecated")
    retired = PermissibleValue(text="retired")

    _defn = EnumDefinition(
        name="LifecycleStatusEnum",
    )

class ApprovalStatusEnum(EnumDefinitionImpl):

    proposed = PermissibleValue(text="proposed")
    approved = PermissibleValue(text="approved")
    rejected = PermissibleValue(text="rejected")
    superseded = PermissibleValue(text="superseded")

    _defn = EnumDefinition(
        name="ApprovalStatusEnum",
    )

class ModelLevelEnum(EnumDefinitionImpl):

    conceptual = PermissibleValue(text="conceptual")
    logical = PermissibleValue(text="logical")
    physical = PermissibleValue(text="physical")

    _defn = EnumDefinition(
        name="ModelLevelEnum",
    )

class EntityTypeEnum(EnumDefinitionImpl):
    """
    Роль логической сущности в модели решения.
    """
    core = PermissibleValue(
        text="core",
        description="Базовая сущность, создаваемая и управляемая решением.")
    derived = PermissibleValue(
        text="derived",
        description="Производная сущность, вычисляемая или агрегируемая из других данных.")
    reference = PermissibleValue(
        text="reference",
        description="Справочная сущность или представление управляемого справочника.")

    _defn = EnumDefinition(
        name="EntityTypeEnum",
        description="Роль логической сущности в модели решения.",
    )

class DataClassEnum(EnumDefinitionImpl):
    """
    Класс данных для наследования модельной спецификацией дата-контракта; не совпадает с entity_type.
    """
    reference_data = PermissibleValue(
        text="reference_data",
        description="Нормативно-справочная информация (НСИ).")
    master_data = PermissibleValue(
        text="master_data",
        description="Мастер-данные.")
    transactional_data = PermissibleValue(
        text="transactional_data",
        description="Транзакционные данные.")
    analytical_data = PermissibleValue(
        text="analytical_data",
        description="Аналитические или производные наборы данных.")
    metadata = PermissibleValue(
        text="metadata",
        description="Метаданные.")

    _defn = EnumDefinition(
        name="DataClassEnum",
        description="Класс данных для наследования модельной спецификацией дата-контракта; не совпадает с entity_type.",
    )

class BusinessImportanceEnum(EnumDefinitionImpl):

    high = PermissibleValue(text="high")
    medium = PermissibleValue(text="medium")
    low = PermissibleValue(text="low")

    _defn = EnumDefinition(
        name="BusinessImportanceEnum",
    )

class GovernanceClassificationEnum(EnumDefinitionImpl):
    """
    Базовая шкала ограничения доступа; специальные виды тайны задаются отдельными терминами классификации.
    """
    public = PermissibleValue(text="public")
    internal = PermissibleValue(text="internal")
    confidential = PermissibleValue(text="confidential")
    restricted = PermissibleValue(text="restricted")

    _defn = EnumDefinition(
        name="GovernanceClassificationEnum",
        description="""Базовая шкала ограничения доступа; специальные виды тайны задаются отдельными терминами классификации.""",
    )

class LogicalDataTypeEnum(EnumDefinitionImpl):

    string = PermissibleValue(text="string")
    integer = PermissibleValue(text="integer")
    decimal = PermissibleValue(text="decimal")
    boolean = PermissibleValue(text="boolean")
    date = PermissibleValue(text="date")
    datetime = PermissibleValue(text="datetime")
    time = PermissibleValue(text="time")
    binary = PermissibleValue(text="binary")
    identifier = PermissibleValue(text="identifier")
    uri = PermissibleValue(text="uri")
    object = PermissibleValue(text="object")

    _defn = EnumDefinition(
        name="LogicalDataTypeEnum",
    )

class PhysicalObjectKindEnum(EnumDefinitionImpl):

    database = PermissibleValue(text="database")
    schema = PermissibleValue(text="schema")
    table = PermissibleValue(text="table")
    view = PermissibleValue(text="view")
    column = PermissibleValue(text="column")
    api = PermissibleValue(text="api")
    endpoint = PermissibleValue(text="endpoint")
    payload = PermissibleValue(text="payload")
    topic = PermissibleValue(text="topic")
    queue = PermissibleValue(text="queue")
    message = PermissibleValue(text="message")
    file = PermissibleValue(text="file")
    dataset = PermissibleValue(text="dataset")
    pipeline = PermissibleValue(text="pipeline")

    _defn = EnumDefinition(
        name="PhysicalObjectKindEnum",
    )

class FlowDirectionEnum(EnumDefinitionImpl):

    inbound = PermissibleValue(text="inbound")
    outbound = PermissibleValue(text="outbound")
    internal = PermissibleValue(text="internal")
    bidirectional = PermissibleValue(text="bidirectional")

    _defn = EnumDefinition(
        name="FlowDirectionEnum",
    )

class SolutionDataRoleEnum(EnumDefinitionImpl):

    producer = PermissibleValue(text="producer")
    consumer = PermissibleValue(text="consumer")
    intermediary = PermissibleValue(text="intermediary")

    _defn = EnumDefinition(
        name="SolutionDataRoleEnum",
    )

class IntegrationChannelEnum(EnumDefinitionImpl):

    api = PermissibleValue(text="api")
    queue = PermissibleValue(text="queue")
    database = PermissibleValue(text="database")
    file = PermissibleValue(text="file")
    other = PermissibleValue(text="other")

    _defn = EnumDefinition(
        name="IntegrationChannelEnum",
    )

class IntegrationClassEnum(EnumDefinitionImpl):

    EAP = PermissibleValue(text="EAP")
    EDA = PermissibleValue(text="EDA")

    _defn = EnumDefinition(
        name="IntegrationClassEnum",
    )

class IntegrationLevelEnum(EnumDefinitionImpl):

    intraplatform = PermissibleValue(text="intraplatform")
    interplatform = PermissibleValue(text="interplatform")

    _defn = EnumDefinition(
        name="IntegrationLevelEnum",
    )

class MappingTypeEnum(EnumDefinitionImpl):
    """
    Kind of Mapping assertion. realizes = solution element → enterprise conceptual; field_mapping = mapsTo (physical ↔
    logical); aligns_with = enterprise conceptual ↔ external term. Do not use Mapping for SpecImpl implements (that is
    conforms_to / publication implements).
    """
    semantic_equivalence = PermissibleValue(text="semantic_equivalence")
    specialization = PermissibleValue(text="specialization")
    implementation = PermissibleValue(text="implementation")
    field_mapping = PermissibleValue(
        text="field_mapping",
        description="Technical/structural mapsTo between physical and logical.")
    transformation = PermissibleValue(text="transformation")
    aggregation = PermissibleValue(text="aggregation")
    derivation = PermissibleValue(text="derivation")
    realizes = PermissibleValue(
        text="realizes",
        description="Solution logical/concept realizes an enterprise conceptual entity.")
    aligns_with = PermissibleValue(
        text="aligns_with",
        description="Enterprise conceptual aligns with an external reference term.")

    _defn = EnumDefinition(
        name="MappingTypeEnum",
        description="""Kind of Mapping assertion. realizes = solution element → enterprise conceptual; field_mapping = mapsTo (physical ↔ logical); aligns_with = enterprise conceptual ↔ external term. Do not use Mapping for SpecImpl implements (that is conforms_to / publication implements).""",
    )

class ImplementationProfileEnum(EnumDefinitionImpl):
    """
    DAMS-side mirror of kernel ImplementationProfile for ModelPackage metadata. Package-level dams_model_level applies
    only to dams-data-model.
    """
    other = PermissibleValue(text="other")

    _defn = EnumDefinition(
        name="ImplementationProfileEnum",
        description="""DAMS-side mirror of kernel ImplementationProfile for ModelPackage metadata. Package-level dams_model_level applies only to dams-data-model.""",
    )

    @classmethod
    def _addvals(cls):
        setattr(cls, "dams-data-model",
            PermissibleValue(
                text="dams-data-model",
                description="MOEX DAMS corporate data-model implementation."))
        setattr(cls, "ontology-application",
            PermissibleValue(
                text="ontology-application",
                description="Not a DAMS model Impl — ontology application profile."))
        setattr(cls, "api-specification",
            PermissibleValue(text="api-specification"))
        setattr(cls, "data-contract",
            PermissibleValue(text="data-contract"))

class DAMSModelLevelEnum(EnumDefinitionImpl):
    """
    Package-level DAMS model layer (ADR-021). Distinct from ModelLevelEnum (element conceptual/logical/physical). No
    domain-logical value.
    """
    solution = PermissibleValue(
        text="solution",
        description="IT-solution model with local logical/physical facets.")

    _defn = EnumDefinition(
        name="DAMSModelLevelEnum",
        description="""Package-level DAMS model layer (ADR-021). Distinct from ModelLevelEnum (element conceptual/logical/physical). No domain-logical value.""",
    )

    @classmethod
    def _addvals(cls):
        setattr(cls, "enterprise-conceptual",
            PermissibleValue(
                text="enterprise-conceptual",
                description="Enterprise corporate conceptual model (solution-independent)."))

class ImplementationScopeEnum(EnumDefinitionImpl):

    enterprise = PermissibleValue(
        text="enterprise",
        description="Enterprise-wide scope (no solution_ref).")
    solution = PermissibleValue(
        text="solution",
        description="Scoped to a specific IT solution.")

    _defn = EnumDefinition(
        name="ImplementationScopeEnum",
    )

class MappingCardinalityEnum(EnumDefinitionImpl):

    one_to_one = PermissibleValue(text="one_to_one")
    one_to_many = PermissibleValue(text="one_to_many")
    many_to_one = PermissibleValue(text="many_to_one")
    many_to_many = PermissibleValue(text="many_to_many")

    _defn = EnumDefinition(
        name="MappingCardinalityEnum",
    )

class CompatibilityModeEnum(EnumDefinitionImpl):

    backward = PermissibleValue(text="backward")
    forward = PermissibleValue(text="forward")
    full = PermissibleValue(text="full")
    none = PermissibleValue(text="none")

    _defn = EnumDefinition(
        name="CompatibilityModeEnum",
    )

class SpecificationKindEnum(EnumDefinitionImpl):

    integration = PermissibleValue(text="integration")
    data_model = PermissibleValue(text="data_model")
    data_quality = PermissibleValue(text="data_quality")

    _defn = EnumDefinition(
        name="SpecificationKindEnum",
    )

class EnforcementResultEnum(EnumDefinitionImpl):

    warn = PermissibleValue(text="warn")
    fail = PermissibleValue(text="fail")
    not_applicable = PermissibleValue(text="not_applicable")

    _defn = EnumDefinition(
        name="EnforcementResultEnum",
    )

    @classmethod
    def _addvals(cls):
        setattr(cls, "pass",
            PermissibleValue(text="pass"))

class RequirementLevelEnum(EnumDefinitionImpl):
    """
    Уровень применения требования к спецификации.
    """
    conceptual_model = PermissibleValue(
        text="conceptual_model",
        description="Концептуальная модель")
    it_solution = PermissibleValue(
        text="it_solution",
        description="ИТ-решение")
    it_system = PermissibleValue(
        text="it_system",
        description="ИТ-система")

    _defn = EnumDefinition(
        name="RequirementLevelEnum",
        description="Уровень применения требования к спецификации.",
    )

class RequirementSectionEnum(EnumDefinitionImpl):
    """
    Раздел каталога требований (трёхбуквенный код в code).
    """
    LDM = PermissibleValue(
        text="LDM",
        description="Логическая модель")
    PDM = PermissibleValue(
        text="PDM",
        description="Физическая модель")
    REF = PermissibleValue(
        text="REF",
        description="Связи сущностей")
    ATR = PermissibleValue(
        text="ATR",
        description="Атрибуты")
    FLW = PermissibleValue(
        text="FLW",
        description="Потоки данных")
    CLS = PermissibleValue(
        text="CLS",
        description="Классификация данных")
    GEN = PermissibleValue(
        text="GEN",
        description="Общие требования")

    _defn = EnumDefinition(
        name="RequirementSectionEnum",
        description="Раздел каталога требований (трёхбуквенный код в code).",
    )

class FormalCheckKindEnum(EnumDefinitionImpl):
    """
    Вид формальной проверки в нотации, близкой к LinkML constraints.
    """
    slot_required = PermissibleValue(text="slot_required")
    slot_min_cardinality = PermissibleValue(text="slot_min_cardinality")
    ref_resolves = PermissibleValue(text="ref_resolves")
    key_subset = PermissibleValue(text="key_subset")
    custom = PermissibleValue(text="custom")

    _defn = EnumDefinition(
        name="FormalCheckKindEnum",
        description="Вид формальной проверки в нотации, близкой к LinkML constraints.",
    )

class CheckSeverityEnum(EnumDefinitionImpl):

    error = PermissibleValue(text="error")
    warning = PermissibleValue(text="warning")

    _defn = EnumDefinition(
        name="CheckSeverityEnum",
    )

# Slots
class slots:
    pass

slots.repository_id = Slot(uri=DAMS.repository_id, name="repository_id", curie=DAMS.curie('repository_id'),
                   model_uri=DAMS.repository_id, domain=None, range=URIRef)

slots.registry_entries = Slot(uri=DAMS.registry_entries, name="registry_entries", curie=DAMS.curie('registry_entries'),
                   model_uri=DAMS.registry_entries, domain=None, range=Optional[Union[dict[Union[str, RegistryEntryRegistryId], Union[dict, RegistryEntry]], list[Union[dict, RegistryEntry]]]])

slots.model_packages = Slot(uri=DAMS.model_packages, name="model_packages", curie=DAMS.curie('model_packages'),
                   model_uri=DAMS.model_packages, domain=None, range=Optional[Union[dict[Union[str, ModelPackageElementId], Union[dict, ModelPackage]], list[Union[dict, ModelPackage]]]])

slots.data_flows = Slot(uri=DAMS.data_flows, name="data_flows", curie=DAMS.curie('data_flows'),
                   model_uri=DAMS.data_flows, domain=None, range=Optional[Union[dict[Union[str, DataFlowElementId], Union[dict, DataFlow]], list[Union[dict, DataFlow]]]])

slots.data_model_bindings = Slot(uri=DAMS.data_model_bindings, name="data_model_bindings", curie=DAMS.curie('data_model_bindings'),
                   model_uri=DAMS.data_model_bindings, domain=None, range=Optional[Union[dict[Union[str, DataModelBindingElementId], Union[dict, DataModelBinding]], list[Union[dict, DataModelBinding]]]])

slots.metrics = Slot(uri=DAMS.metrics, name="metrics", curie=DAMS.curie('metrics'),
                   model_uri=DAMS.metrics, domain=None, range=Optional[Union[dict[Union[str, MetricElementId], Union[dict, Metric]], list[Union[dict, Metric]]]])

slots.dimensions = Slot(uri=DAMS.dimensions, name="dimensions", curie=DAMS.curie('dimensions'),
                   model_uri=DAMS.dimensions, domain=None, range=Optional[Union[dict[Union[str, DimensionElementId], Union[dict, Dimension]], list[Union[dict, Dimension]]]])

slots.classification_assignments = Slot(uri=DAMS.classification_assignments, name="classification_assignments", curie=DAMS.curie('classification_assignments'),
                   model_uri=DAMS.classification_assignments, domain=None, range=Optional[Union[dict[Union[str, ClassificationAssignmentAssignmentId], Union[dict, ClassificationAssignment]], list[Union[dict, ClassificationAssignment]]]])

slots.policy_bindings = Slot(uri=DAMS.policy_bindings, name="policy_bindings", curie=DAMS.curie('policy_bindings'),
                   model_uri=DAMS.policy_bindings, domain=None, range=Optional[Union[dict[Union[str, PolicyBindingPolicyBindingId], Union[dict, PolicyBinding]], list[Union[dict, PolicyBinding]]]])

slots.registry_id = Slot(uri=DAMS.registry_id, name="registry_id", curie=DAMS.curie('registry_id'),
                   model_uri=DAMS.registry_id, domain=None, range=URIRef)

slots.registry_name = Slot(uri=DAMS.registry_name, name="registry_name", curie=DAMS.curie('registry_name'),
                   model_uri=DAMS.registry_name, domain=None, range=str)

slots.registry_description = Slot(uri=DAMS.registry_description, name="registry_description", curie=DAMS.curie('registry_description'),
                   model_uri=DAMS.registry_description, domain=None, range=Optional[str])

slots.master_system = Slot(uri=DAMS.master_system, name="master_system", curie=DAMS.curie('master_system'),
                   model_uri=DAMS.master_system, domain=None, range=str)

slots.source_uri = Slot(uri=DAMS.source_uri, name="source_uri", curie=DAMS.curie('source_uri'),
                   model_uri=DAMS.source_uri, domain=None, range=Optional[Union[str, URI]])

slots.registry_status = Slot(uri=DAMS.registry_status, name="registry_status", curie=DAMS.curie('registry_status'),
                   model_uri=DAMS.registry_status, domain=None, range=Union[str, "LifecycleStatusEnum"])

slots.member_system_refs = Slot(uri=DAMS.member_system_refs, name="member_system_refs", curie=DAMS.curie('member_system_refs'),
                   model_uri=DAMS.member_system_refs, domain=None, range=Optional[Union[Union[str, ITSystemRegistryId], list[Union[str, ITSystemRegistryId]]]])

slots.platform_ref = Slot(uri=DAMS.platform_ref, name="platform_ref", curie=DAMS.curie('platform_ref'),
                   model_uri=DAMS.platform_ref, domain=None, range=Optional[Union[str, ITPlatformRegistryId]])

slots.parent_domain_ref = Slot(uri=DAMS.parent_domain_ref, name="parent_domain_ref", curie=DAMS.curie('parent_domain_ref'),
                   model_uri=DAMS.parent_domain_ref, domain=None, range=Optional[Union[str, BusinessDomainRegistryId]])

slots.assignment_id = Slot(uri=DAMS.assignment_id, name="assignment_id", curie=DAMS.curie('assignment_id'),
                   model_uri=DAMS.assignment_id, domain=None, range=URIRef)

slots.classified_element_ref = Slot(uri=DAMS.classified_element_ref, name="classified_element_ref", curie=DAMS.curie('classified_element_ref'),
                   model_uri=DAMS.classified_element_ref, domain=None, range=Union[str, URIorCURIE])

slots.classification_term_ref = Slot(uri=DAMS.classification_term_ref, name="classification_term_ref", curie=DAMS.curie('classification_term_ref'),
                   model_uri=DAMS.classification_term_ref, domain=None, range=Optional[Union[str, DataClassificationTermRegistryId]])

slots.policy_binding_id = Slot(uri=DAMS.policy_binding_id, name="policy_binding_id", curie=DAMS.curie('policy_binding_id'),
                   model_uri=DAMS.policy_binding_id, domain=None, range=URIRef)

slots.policy_target_ref = Slot(uri=DAMS.policy_target_ref, name="policy_target_ref", curie=DAMS.curie('policy_target_ref'),
                   model_uri=DAMS.policy_target_ref, domain=None, range=Union[str, URIorCURIE])

slots.policy_ref = Slot(uri=DAMS.policy_ref, name="policy_ref", curie=DAMS.curie('policy_ref'),
                   model_uri=DAMS.policy_ref, domain=None, range=Union[str, PolicyRegistryId])

slots.lifecycle_status = Slot(uri=DAMS.lifecycle_status, name="lifecycle_status", curie=DAMS.curie('lifecycle_status'),
                   model_uri=DAMS.lifecycle_status, domain=None, range=Union[str, "LifecycleStatusEnum"])

slots.valid_from = Slot(uri=DAMS.valid_from, name="valid_from", curie=DAMS.curie('valid_from'),
                   model_uri=DAMS.valid_from, domain=None, range=Optional[Union[str, XSDDateTime]])

slots.valid_to = Slot(uri=DAMS.valid_to, name="valid_to", curie=DAMS.curie('valid_to'),
                   model_uri=DAMS.valid_to, domain=None, range=Optional[Union[str, XSDDateTime]])

slots.deprecated_by_ref = Slot(uri=DAMS.deprecated_by_ref, name="deprecated_by_ref", curie=DAMS.curie('deprecated_by_ref'),
                   model_uri=DAMS.deprecated_by_ref, domain=None, range=Optional[Union[str, URIorCURIE]])

slots.data_owner_ref = Slot(uri=DAMS.data_owner_ref, name="data_owner_ref", curie=DAMS.curie('data_owner_ref'),
                   model_uri=DAMS.data_owner_ref, domain=None, range=Optional[Union[str, RoleRegistryId]])

slots.data_steward_ref = Slot(uri=DAMS.data_steward_ref, name="data_steward_ref", curie=DAMS.curie('data_steward_ref'),
                   model_uri=DAMS.data_steward_ref, domain=None, range=Optional[Union[str, RoleRegistryId]])

slots.owning_unit_ref = Slot(uri=DAMS.owning_unit_ref, name="owning_unit_ref", curie=DAMS.curie('owning_unit_ref'),
                   model_uri=DAMS.owning_unit_ref, domain=None, range=Optional[Union[str, OrganizationUnitRegistryId]])

slots.entity_type = Slot(uri=DAMS.entity_type, name="entity_type", curie=DAMS.curie('entity_type'),
                   model_uri=DAMS.entity_type, domain=None, range=Optional[Union[str, "EntityTypeEnum"]])

slots.data_class = Slot(uri=DAMS.data_class, name="data_class", curie=DAMS.curie('data_class'),
                   model_uri=DAMS.data_class, domain=None, range=Optional[Union[str, "DataClassEnum"]])

slots.business_importance = Slot(uri=DAMS.business_importance, name="business_importance", curie=DAMS.curie('business_importance'),
                   model_uri=DAMS.business_importance, domain=None, range=Optional[Union[str, "BusinessImportanceEnum"]])

slots.governance_classification = Slot(uri=DAMS.governance_classification, name="governance_classification", curie=DAMS.curie('governance_classification'),
                   model_uri=DAMS.governance_classification, domain=None, range=Optional[Union[str, "GovernanceClassificationEnum"]])

slots.sensitivity_term_refs = Slot(uri=DAMS.sensitivity_term_refs, name="sensitivity_term_refs", curie=DAMS.curie('sensitivity_term_refs'),
                   model_uri=DAMS.sensitivity_term_refs, domain=None, range=Optional[Union[Union[str, DataClassificationTermRegistryId], list[Union[str, DataClassificationTermRegistryId]]]])

slots.classification_source = Slot(uri=DAMS.classification_source, name="classification_source", curie=DAMS.curie('classification_source'),
                   model_uri=DAMS.classification_source, domain=None, range=Optional[str])

slots.classification_rationale = Slot(uri=DAMS.classification_rationale, name="classification_rationale", curie=DAMS.curie('classification_rationale'),
                   model_uri=DAMS.classification_rationale, domain=None, range=Optional[str])

slots.policy_refs = Slot(uri=DAMS.policy_refs, name="policy_refs", curie=DAMS.curie('policy_refs'),
                   model_uri=DAMS.policy_refs, domain=None, range=Optional[Union[Union[str, PolicyRegistryId], list[Union[str, PolicyRegistryId]]]])

slots.source_artifact_ref = Slot(uri=DAMS.source_artifact_ref, name="source_artifact_ref", curie=DAMS.curie('source_artifact_ref'),
                   model_uri=DAMS.source_artifact_ref, domain=None, range=Optional[Union[str, URI]])

slots.evidence_refs = Slot(uri=DAMS.evidence_refs, name="evidence_refs", curie=DAMS.curie('evidence_refs'),
                   model_uri=DAMS.evidence_refs, domain=None, range=Optional[Union[Union[str, URI], list[Union[str, URI]]]])

slots.approval_status = Slot(uri=DAMS.approval_status, name="approval_status", curie=DAMS.curie('approval_status'),
                   model_uri=DAMS.approval_status, domain=None, range=Optional[Union[str, "ApprovalStatusEnum"]])

slots.approved_by_ref = Slot(uri=DAMS.approved_by_ref, name="approved_by_ref", curie=DAMS.curie('approved_by_ref'),
                   model_uri=DAMS.approved_by_ref, domain=None, range=Optional[Union[str, RoleRegistryId]])

slots.approved_at = Slot(uri=DAMS.approved_at, name="approved_at", curie=DAMS.curie('approved_at'),
                   model_uri=DAMS.approved_at, domain=None, range=Optional[Union[str, XSDDateTime]])

slots.element_id = Slot(uri=DAMS.element_id, name="element_id", curie=DAMS.curie('element_id'),
                   model_uri=DAMS.element_id, domain=None, range=URIRef)

slots.name = Slot(uri=DAMS.name, name="name", curie=DAMS.curie('name'),
                   model_uri=DAMS.name, domain=None, range=str)

slots.title = Slot(uri=DAMS.title, name="title", curie=DAMS.curie('title'),
                   model_uri=DAMS.title, domain=None, range=Optional[str])

slots.description = Slot(uri=DAMS.description, name="description", curie=DAMS.curie('description'),
                   model_uri=DAMS.description, domain=None, range=str)

slots.aliases = Slot(uri=DAMS.aliases, name="aliases", curie=DAMS.curie('aliases'),
                   model_uri=DAMS.aliases, domain=None, range=Optional[Union[str, list[str]]])

slots.glossary_term_refs = Slot(uri=DAMS.glossary_term_refs, name="glossary_term_refs", curie=DAMS.curie('glossary_term_refs'),
                   model_uri=DAMS.glossary_term_refs, domain=None, range=Optional[Union[Union[str, GlossaryTermRegistryId], list[Union[str, GlossaryTermRegistryId]]]])

slots.tags = Slot(uri=DAMS.tags, name="tags", curie=DAMS.curie('tags'),
                   model_uri=DAMS.tags, domain=None, range=Optional[Union[str, list[str]]])

slots.api_version = Slot(uri=DAMS.api_version, name="api_version", curie=DAMS.curie('api_version'),
                   model_uri=DAMS.api_version, domain=None, range=str)

slots.model_version = Slot(uri=DAMS.model_version, name="model_version", curie=DAMS.curie('model_version'),
                   model_uri=DAMS.model_version, domain=None, range=Union[str, SemVer])

slots.implementation_scope = Slot(uri=DAMS.implementation_scope, name="implementation_scope", curie=DAMS.curie('implementation_scope'),
                   model_uri=DAMS.implementation_scope, domain=None, range=Optional[Union[str, "ImplementationScopeEnum"]])

slots.conceptual_implementation_ref = Slot(uri=DAMS.conceptual_implementation_ref, name="conceptual_implementation_ref", curie=DAMS.curie('conceptual_implementation_ref'),
                   model_uri=DAMS.conceptual_implementation_ref, domain=None, range=Optional[Union[str, URIorCURIE]])

slots.solution_ref = Slot(uri=DAMS.solution_ref, name="solution_ref", curie=DAMS.curie('solution_ref'),
                   model_uri=DAMS.solution_ref, domain=None, range=Optional[Union[str, ITSolutionRegistryId]])

slots.domain_refs = Slot(uri=DAMS.domain_refs, name="domain_refs", curie=DAMS.curie('domain_refs'),
                   model_uri=DAMS.domain_refs, domain=None, range=Optional[Union[Union[str, BusinessDomainRegistryId], list[Union[str, BusinessDomainRegistryId]]]])

slots.imports_refs = Slot(uri=DAMS.imports_refs, name="imports_refs", curie=DAMS.curie('imports_refs'),
                   model_uri=DAMS.imports_refs, domain=None, range=Optional[Union[Union[str, URI], list[Union[str, URI]]]])

slots.conceptual_entities = Slot(uri=DAMS.conceptual_entities, name="conceptual_entities", curie=DAMS.curie('conceptual_entities'),
                   model_uri=DAMS.conceptual_entities, domain=None, range=Optional[Union[dict[Union[str, ConceptualEntityElementId], Union[dict, ConceptualEntity]], list[Union[dict, ConceptualEntity]]]])

slots.domain_contexts = Slot(uri=DAMS.domain_contexts, name="domain_contexts", curie=DAMS.curie('domain_contexts'),
                   model_uri=DAMS.domain_contexts, domain=None, range=Optional[Union[dict[Union[str, DomainContextElementId], Union[dict, DomainContext]], list[Union[dict, DomainContext]]]])

slots.logical_entities = Slot(uri=DAMS.logical_entities, name="logical_entities", curie=DAMS.curie('logical_entities'),
                   model_uri=DAMS.logical_entities, domain=None, range=Optional[Union[dict[Union[str, LogicalEntityElementId], Union[dict, LogicalEntity]], list[Union[dict, LogicalEntity]]]])

slots.relationships = Slot(uri=DAMS.relationships, name="relationships", curie=DAMS.curie('relationships'),
                   model_uri=DAMS.relationships, domain=None, range=Optional[Union[dict[Union[str, RelationshipElementId], Union[dict, Relationship]], list[Union[dict, Relationship]]]])

slots.physical_objects = Slot(uri=DAMS.physical_objects, name="physical_objects", curie=DAMS.curie('physical_objects'),
                   model_uri=DAMS.physical_objects, domain=None, range=Optional[Union[dict[Union[str, PhysicalObjectElementId], Union[dict, PhysicalObject]], list[Union[dict, PhysicalObject]]]])

slots.mappings = Slot(uri=DAMS.mappings, name="mappings", curie=DAMS.curie('mappings'),
                   model_uri=DAMS.mappings, domain=None, range=Optional[Union[dict[Union[str, MappingElementId], Union[dict, Mapping]], list[Union[dict, Mapping]]]])

slots.domain_ref = Slot(uri=DAMS.domain_ref, name="domain_ref", curie=DAMS.curie('domain_ref'),
                   model_uri=DAMS.domain_ref, domain=None, range=Union[str, BusinessDomainRegistryId])

slots.namespace = Slot(uri=DAMS.namespace, name="namespace", curie=DAMS.curie('namespace'),
                   model_uri=DAMS.namespace, domain=None, range=Union[str, URI])

slots.business_process_refs = Slot(uri=DAMS.business_process_refs, name="business_process_refs", curie=DAMS.curie('business_process_refs'),
                   model_uri=DAMS.business_process_refs, domain=None, range=Optional[Union[Union[str, BusinessProcessRegistryId], list[Union[str, BusinessProcessRegistryId]]]])

slots.parent_concept_ref = Slot(uri=DAMS.parent_concept_ref, name="parent_concept_ref", curie=DAMS.curie('parent_concept_ref'),
                   model_uri=DAMS.parent_concept_ref, domain=None, range=Optional[Union[str, ConceptualEntityElementId]])

slots.key_attribute_refs = Slot(uri=DAMS.key_attribute_refs, name="key_attribute_refs", curie=DAMS.curie('key_attribute_refs'),
                   model_uri=DAMS.key_attribute_refs, domain=None, range=Optional[Union[Union[str, URIorCURIE], list[Union[str, URIorCURIE]]]])

slots.context_ref = Slot(uri=DAMS.context_ref, name="context_ref", curie=DAMS.curie('context_ref'),
                   model_uri=DAMS.context_ref, domain=None, range=Union[str, DomainContextElementId])

slots.conceptual_entity_refs = Slot(uri=DAMS.conceptual_entity_refs, name="conceptual_entity_refs", curie=DAMS.curie('conceptual_entity_refs'),
                   model_uri=DAMS.conceptual_entity_refs, domain=None, range=Optional[Union[Union[str, ConceptualEntityElementId], list[Union[str, ConceptualEntityElementId]]]])

slots.solution_data_role = Slot(uri=DAMS.solution_data_role, name="solution_data_role", curie=DAMS.curie('solution_data_role'),
                   model_uri=DAMS.solution_data_role, domain=None, range=Union[str, "SolutionDataRoleEnum"])

slots.attributes = Slot(uri=DAMS.attributes, name="attributes", curie=DAMS.curie('attributes'),
                   model_uri=DAMS.attributes, domain=None, range=Optional[Union[dict[Union[str, LogicalAttributeElementId], Union[dict, LogicalAttribute]], list[Union[dict, LogicalAttribute]]]])

slots.invariant_refs = Slot(uri=DAMS.invariant_refs, name="invariant_refs", curie=DAMS.curie('invariant_refs'),
                   model_uri=DAMS.invariant_refs, domain=None, range=Optional[Union[Union[str, PolicyRegistryId], list[Union[str, PolicyRegistryId]]]])

slots.owner_entity_ref = Slot(uri=DAMS.owner_entity_ref, name="owner_entity_ref", curie=DAMS.curie('owner_entity_ref'),
                   model_uri=DAMS.owner_entity_ref, domain=None, range=Union[str, LogicalEntityElementId])

slots.logical_type = Slot(uri=DAMS.logical_type, name="logical_type", curie=DAMS.curie('logical_type'),
                   model_uri=DAMS.logical_type, domain=None, range=Union[str, "LogicalDataTypeEnum"])

slots.required = Slot(uri=DAMS.required, name="required", curie=DAMS.curie('required'),
                   model_uri=DAMS.required, domain=None, range=Union[bool, Bool])

slots.multivalued = Slot(uri=DAMS.multivalued, name="multivalued", curie=DAMS.curie('multivalued'),
                   model_uri=DAMS.multivalued, domain=None, range=Union[bool, Bool])

slots.minimum_cardinality = Slot(uri=DAMS.minimum_cardinality, name="minimum_cardinality", curie=DAMS.curie('minimum_cardinality'),
                   model_uri=DAMS.minimum_cardinality, domain=None, range=Optional[int])

slots.maximum_cardinality = Slot(uri=DAMS.maximum_cardinality, name="maximum_cardinality", curie=DAMS.curie('maximum_cardinality'),
                   model_uri=DAMS.maximum_cardinality, domain=None, range=Optional[int])

slots.value_set_ref = Slot(uri=DAMS.value_set_ref, name="value_set_ref", curie=DAMS.curie('value_set_ref'),
                   model_uri=DAMS.value_set_ref, domain=None, range=Optional[Union[str, URI]])

slots.format_pattern = Slot(uri=DAMS.format_pattern, name="format_pattern", curie=DAMS.curie('format_pattern'),
                   model_uri=DAMS.format_pattern, domain=None, range=Optional[str])

slots.default_value = Slot(uri=DAMS.default_value, name="default_value", curie=DAMS.curie('default_value'),
                   model_uri=DAMS.default_value, domain=None, range=Optional[str])

slots.derived_expression = Slot(uri=DAMS.derived_expression, name="derived_expression", curie=DAMS.curie('derived_expression'),
                   model_uri=DAMS.derived_expression, domain=None, range=Optional[str])

slots.source_entity_ref = Slot(uri=DAMS.source_entity_ref, name="source_entity_ref", curie=DAMS.curie('source_entity_ref'),
                   model_uri=DAMS.source_entity_ref, domain=None, range=Union[str, URIorCURIE])

slots.target_entity_ref = Slot(uri=DAMS.target_entity_ref, name="target_entity_ref", curie=DAMS.curie('target_entity_ref'),
                   model_uri=DAMS.target_entity_ref, domain=None, range=Union[str, URIorCURIE])

slots.source_role = Slot(uri=DAMS.source_role, name="source_role", curie=DAMS.curie('source_role'),
                   model_uri=DAMS.source_role, domain=None, range=Optional[str])

slots.target_role = Slot(uri=DAMS.target_role, name="target_role", curie=DAMS.curie('target_role'),
                   model_uri=DAMS.target_role, domain=None, range=Optional[str])

slots.source_min_cardinality = Slot(uri=DAMS.source_min_cardinality, name="source_min_cardinality", curie=DAMS.curie('source_min_cardinality'),
                   model_uri=DAMS.source_min_cardinality, domain=None, range=Optional[int])

slots.source_max_cardinality = Slot(uri=DAMS.source_max_cardinality, name="source_max_cardinality", curie=DAMS.curie('source_max_cardinality'),
                   model_uri=DAMS.source_max_cardinality, domain=None, range=Optional[int])

slots.target_min_cardinality = Slot(uri=DAMS.target_min_cardinality, name="target_min_cardinality", curie=DAMS.curie('target_min_cardinality'),
                   model_uri=DAMS.target_min_cardinality, domain=None, range=Optional[int])

slots.target_max_cardinality = Slot(uri=DAMS.target_max_cardinality, name="target_max_cardinality", curie=DAMS.curie('target_max_cardinality'),
                   model_uri=DAMS.target_max_cardinality, domain=None, range=Optional[int])

slots.identifying = Slot(uri=DAMS.identifying, name="identifying", curie=DAMS.curie('identifying'),
                   model_uri=DAMS.identifying, domain=None, range=Optional[Union[bool, Bool]])

slots.associative = Slot(uri=DAMS.associative, name="associative", curie=DAMS.curie('associative'),
                   model_uri=DAMS.associative, domain=None, range=Optional[Union[bool, Bool]])

slots.system_ref = Slot(uri=DAMS.system_ref, name="system_ref", curie=DAMS.curie('system_ref'),
                   model_uri=DAMS.system_ref, domain=None, range=Union[str, ITSystemRegistryId])

slots.object_kind = Slot(uri=DAMS.object_kind, name="object_kind", curie=DAMS.curie('object_kind'),
                   model_uri=DAMS.object_kind, domain=None, range=Union[str, "PhysicalObjectKindEnum"])

slots.qualified_name = Slot(uri=DAMS.qualified_name, name="qualified_name", curie=DAMS.curie('qualified_name'),
                   model_uri=DAMS.qualified_name, domain=None, range=str)

slots.technology = Slot(uri=DAMS.technology, name="technology", curie=DAMS.curie('technology'),
                   model_uri=DAMS.technology, domain=None, range=str)

slots.native_schema_ref = Slot(uri=DAMS.native_schema_ref, name="native_schema_ref", curie=DAMS.curie('native_schema_ref'),
                   model_uri=DAMS.native_schema_ref, domain=None, range=Union[str, URI])

slots.direction = Slot(uri=DAMS.direction, name="direction", curie=DAMS.curie('direction'),
                   model_uri=DAMS.direction, domain=None, range=Union[str, "FlowDirectionEnum"])

slots.physical_fields = Slot(uri=DAMS.physical_fields, name="physical_fields", curie=DAMS.curie('physical_fields'),
                   model_uri=DAMS.physical_fields, domain=None, range=Optional[Union[dict[Union[str, PhysicalFieldElementId], Union[dict, PhysicalField]], list[Union[dict, PhysicalField]]]])

slots.physical_object_ref = Slot(uri=DAMS.physical_object_ref, name="physical_object_ref", curie=DAMS.curie('physical_object_ref'),
                   model_uri=DAMS.physical_object_ref, domain=None, range=Union[str, PhysicalObjectElementId])

slots.native_name = Slot(uri=DAMS.native_name, name="native_name", curie=DAMS.curie('native_name'),
                   model_uri=DAMS.native_name, domain=None, range=str)

slots.native_type = Slot(uri=DAMS.native_type, name="native_type", curie=DAMS.curie('native_type'),
                   model_uri=DAMS.native_type, domain=None, range=str)

slots.ordinal_position = Slot(uri=DAMS.ordinal_position, name="ordinal_position", curie=DAMS.curie('ordinal_position'),
                   model_uri=DAMS.ordinal_position, domain=None, range=Optional[int])

slots.schema_path = Slot(uri=DAMS.schema_path, name="schema_path", curie=DAMS.curie('schema_path'),
                   model_uri=DAMS.schema_path, domain=None, range=Optional[str])

slots.source_refs = Slot(uri=DAMS.source_refs, name="source_refs", curie=DAMS.curie('source_refs'),
                   model_uri=DAMS.source_refs, domain=None, range=Optional[Union[Union[str, URIorCURIE], list[Union[str, URIorCURIE]]]])

slots.target_refs = Slot(uri=DAMS.target_refs, name="target_refs", curie=DAMS.curie('target_refs'),
                   model_uri=DAMS.target_refs, domain=None, range=Optional[Union[Union[str, URIorCURIE], list[Union[str, URIorCURIE]]]])

slots.mapping_type = Slot(uri=DAMS.mapping_type, name="mapping_type", curie=DAMS.curie('mapping_type'),
                   model_uri=DAMS.mapping_type, domain=None, range=Union[str, "MappingTypeEnum"])

slots.mapping_cardinality = Slot(uri=DAMS.mapping_cardinality, name="mapping_cardinality", curie=DAMS.curie('mapping_cardinality'),
                   model_uri=DAMS.mapping_cardinality, domain=None, range=Union[str, "MappingCardinalityEnum"])

slots.transformation_ref = Slot(uri=DAMS.transformation_ref, name="transformation_ref", curie=DAMS.curie('transformation_ref'),
                   model_uri=DAMS.transformation_ref, domain=None, range=Optional[Union[str, URI]])

slots.transformation_expression = Slot(uri=DAMS.transformation_expression, name="transformation_expression", curie=DAMS.curie('transformation_expression'),
                   model_uri=DAMS.transformation_expression, domain=None, range=Optional[str])

slots.confidence = Slot(uri=DAMS.confidence, name="confidence", curie=DAMS.curie('confidence'),
                   model_uri=DAMS.confidence, domain=None, range=Optional[Decimal])

slots.integration_ref = Slot(uri=DAMS.integration_ref, name="integration_ref", curie=DAMS.curie('integration_ref'),
                   model_uri=DAMS.integration_ref, domain=None, range=Union[str, IntegrationReferenceRegistryId])

slots.contract_ref = Slot(uri=DAMS.contract_ref, name="contract_ref", curie=DAMS.curie('contract_ref'),
                   model_uri=DAMS.contract_ref, domain=None, range=Optional[Union[str, DataContractReferenceRegistryId]])

slots.source_solution_ref = Slot(uri=DAMS.source_solution_ref, name="source_solution_ref", curie=DAMS.curie('source_solution_ref'),
                   model_uri=DAMS.source_solution_ref, domain=None, range=Union[str, ITSolutionRegistryId])

slots.target_solution_ref = Slot(uri=DAMS.target_solution_ref, name="target_solution_ref", curie=DAMS.curie('target_solution_ref'),
                   model_uri=DAMS.target_solution_ref, domain=None, range=Union[str, ITSolutionRegistryId])

slots.source_system_ref = Slot(uri=DAMS.source_system_ref, name="source_system_ref", curie=DAMS.curie('source_system_ref'),
                   model_uri=DAMS.source_system_ref, domain=None, range=Union[str, ITSystemRegistryId])

slots.target_system_ref = Slot(uri=DAMS.target_system_ref, name="target_system_ref", curie=DAMS.curie('target_system_ref'),
                   model_uri=DAMS.target_system_ref, domain=None, range=Union[str, ITSystemRegistryId])

slots.source_platform_ref = Slot(uri=DAMS.source_platform_ref, name="source_platform_ref", curie=DAMS.curie('source_platform_ref'),
                   model_uri=DAMS.source_platform_ref, domain=None, range=Union[str, ITPlatformRegistryId])

slots.target_platform_ref = Slot(uri=DAMS.target_platform_ref, name="target_platform_ref", curie=DAMS.curie('target_platform_ref'),
                   model_uri=DAMS.target_platform_ref, domain=None, range=Union[str, ITPlatformRegistryId])

slots.integration_level = Slot(uri=DAMS.integration_level, name="integration_level", curie=DAMS.curie('integration_level'),
                   model_uri=DAMS.integration_level, domain=None, range=Union[str, "IntegrationLevelEnum"])

slots.integration_class = Slot(uri=DAMS.integration_class, name="integration_class", curie=DAMS.curie('integration_class'),
                   model_uri=DAMS.integration_class, domain=None, range=Union[str, "IntegrationClassEnum"])

slots.integration_channel = Slot(uri=DAMS.integration_channel, name="integration_channel", curie=DAMS.curie('integration_channel'),
                   model_uri=DAMS.integration_channel, domain=None, range=Union[str, "IntegrationChannelEnum"])

slots.integration_spec_ref = Slot(uri=DAMS.integration_spec_ref, name="integration_spec_ref", curie=DAMS.curie('integration_spec_ref'),
                   model_uri=DAMS.integration_spec_ref, domain=None, range=Union[str, URI])

slots.entity_bindings = Slot(uri=DAMS.entity_bindings, name="entity_bindings", curie=DAMS.curie('entity_bindings'),
                   model_uri=DAMS.entity_bindings, domain=None, range=Optional[Union[dict[Union[str, DataFlowEntityBindingElementId], Union[dict, DataFlowEntityBinding]], list[Union[dict, DataFlowEntityBinding]]]])

slots.flow_ref = Slot(uri=DAMS.flow_ref, name="flow_ref", curie=DAMS.curie('flow_ref'),
                   model_uri=DAMS.flow_ref, domain=None, range=Union[str, DataFlowElementId])

slots.source_model_ref = Slot(uri=DAMS.source_model_ref, name="source_model_ref", curie=DAMS.curie('source_model_ref'),
                   model_uri=DAMS.source_model_ref, domain=None, range=Union[str, URI])

slots.logical_entity_ref = Slot(uri=DAMS.logical_entity_ref, name="logical_entity_ref", curie=DAMS.curie('logical_entity_ref'),
                   model_uri=DAMS.logical_entity_ref, domain=None, range=Union[str, LogicalEntityElementId])

slots.logical_attribute_refs = Slot(uri=DAMS.logical_attribute_refs, name="logical_attribute_refs", curie=DAMS.curie('logical_attribute_refs'),
                   model_uri=DAMS.logical_attribute_refs, domain=None, range=Optional[Union[Union[str, LogicalAttributeElementId], list[Union[str, LogicalAttributeElementId]]]])

slots.physical_object_refs = Slot(uri=DAMS.physical_object_refs, name="physical_object_refs", curie=DAMS.curie('physical_object_refs'),
                   model_uri=DAMS.physical_object_refs, domain=None, range=Optional[Union[Union[str, PhysicalObjectElementId], list[Union[str, PhysicalObjectElementId]]]])

slots.physical_field_refs = Slot(uri=DAMS.physical_field_refs, name="physical_field_refs", curie=DAMS.curie('physical_field_refs'),
                   model_uri=DAMS.physical_field_refs, domain=None, range=Optional[Union[Union[str, PhysicalFieldElementId], list[Union[str, PhysicalFieldElementId]]]])

slots.transformation_mapping_refs = Slot(uri=DAMS.transformation_mapping_refs, name="transformation_mapping_refs", curie=DAMS.curie('transformation_mapping_refs'),
                   model_uri=DAMS.transformation_mapping_refs, domain=None, range=Optional[Union[Union[str, MappingElementId], list[Union[str, MappingElementId]]]])

slots.specification_version = Slot(uri=DAMS.specification_version, name="specification_version", curie=DAMS.curie('specification_version'),
                   model_uri=DAMS.specification_version, domain=None, range=Union[str, SemVer])

slots.implementation_version = Slot(uri=DAMS.implementation_version, name="implementation_version", curie=DAMS.curie('implementation_version'),
                   model_uri=DAMS.implementation_version, domain=None, range=Union[str, SemVer])

slots.model_package_ref = Slot(uri=DAMS.model_package_ref, name="model_package_ref", curie=DAMS.curie('model_package_ref'),
                   model_uri=DAMS.model_package_ref, domain=None, range=Union[str, URI])

slots.model_revision = Slot(uri=DAMS.model_revision, name="model_revision", curie=DAMS.curie('model_revision'),
                   model_uri=DAMS.model_revision, domain=None, range=str)

slots.selections = Slot(uri=DAMS.selections, name="selections", curie=DAMS.curie('selections'),
                   model_uri=DAMS.selections, domain=None, range=Optional[Union[dict[Union[str, ModelSelectionElementId], Union[dict, ModelSelection]], list[Union[dict, ModelSelection]]]])

slots.compatibility_mode = Slot(uri=DAMS.compatibility_mode, name="compatibility_mode", curie=DAMS.curie('compatibility_mode'),
                   model_uri=DAMS.compatibility_mode, domain=None, range=Union[str, "CompatibilityModeEnum"])

slots.compatibility_baseline_ref = Slot(uri=DAMS.compatibility_baseline_ref, name="compatibility_baseline_ref", curie=DAMS.curie('compatibility_baseline_ref'),
                   model_uri=DAMS.compatibility_baseline_ref, domain=None, range=Optional[Union[str, URI]])

slots.integrity_digest = Slot(uri=DAMS.integrity_digest, name="integrity_digest", curie=DAMS.curie('integrity_digest'),
                   model_uri=DAMS.integrity_digest, domain=None, range=Union[str, Sha256Digest])

slots.generated_at = Slot(uri=DAMS.generated_at, name="generated_at", curie=DAMS.curie('generated_at'),
                   model_uri=DAMS.generated_at, domain=None, range=Union[str, XSDDateTime])

slots.selected_entities = Slot(uri=DAMS.selected_entities, name="selected_entities", curie=DAMS.curie('selected_entities'),
                   model_uri=DAMS.selected_entities, domain=None, range=Optional[Union[dict[Union[str, SelectedEntityElementId], Union[dict, SelectedEntity]], list[Union[dict, SelectedEntity]]]])

slots.selected_attributes = Slot(uri=DAMS.selected_attributes, name="selected_attributes", curie=DAMS.curie('selected_attributes'),
                   model_uri=DAMS.selected_attributes, domain=None, range=Optional[Union[dict[Union[str, SelectedAttributeElementId], Union[dict, SelectedAttribute]], list[Union[dict, SelectedAttribute]]]])

slots.logical_attribute_ref = Slot(uri=DAMS.logical_attribute_ref, name="logical_attribute_ref", curie=DAMS.curie('logical_attribute_ref'),
                   model_uri=DAMS.logical_attribute_ref, domain=None, range=Union[str, LogicalAttributeElementId])

slots.transformation_mapping_ref = Slot(uri=DAMS.transformation_mapping_ref, name="transformation_mapping_ref", curie=DAMS.curie('transformation_mapping_ref'),
                   model_uri=DAMS.transformation_mapping_ref, domain=None, range=Optional[Union[str, MappingElementId]])

slots.metric_expression = Slot(uri=DAMS.metric_expression, name="metric_expression", curie=DAMS.curie('metric_expression'),
                   model_uri=DAMS.metric_expression, domain=None, range=str)

slots.aggregation_function = Slot(uri=DAMS.aggregation_function, name="aggregation_function", curie=DAMS.curie('aggregation_function'),
                   model_uri=DAMS.aggregation_function, domain=None, range=str)

slots.grain_entity_refs = Slot(uri=DAMS.grain_entity_refs, name="grain_entity_refs", curie=DAMS.curie('grain_entity_refs'),
                   model_uri=DAMS.grain_entity_refs, domain=None, range=Optional[Union[Union[str, LogicalEntityElementId], list[Union[str, LogicalEntityElementId]]]])

slots.dimension_attribute_refs = Slot(uri=DAMS.dimension_attribute_refs, name="dimension_attribute_refs", curie=DAMS.curie('dimension_attribute_refs'),
                   model_uri=DAMS.dimension_attribute_refs, domain=None, range=Optional[Union[Union[str, LogicalAttributeElementId], list[Union[str, LogicalAttributeElementId]]]])

slots.measure_attribute_refs = Slot(uri=DAMS.measure_attribute_refs, name="measure_attribute_refs", curie=DAMS.curie('measure_attribute_refs'),
                   model_uri=DAMS.measure_attribute_refs, domain=None, range=Optional[Union[Union[str, LogicalAttributeElementId], list[Union[str, LogicalAttributeElementId]]]])

slots.unit = Slot(uri=DAMS.unit, name="unit", curie=DAMS.curie('unit'),
                   model_uri=DAMS.unit, domain=None, range=Optional[str])

slots.filter_expression = Slot(uri=DAMS.filter_expression, name="filter_expression", curie=DAMS.curie('filter_expression'),
                   model_uri=DAMS.filter_expression, domain=None, range=Optional[str])

slots.check_id = Slot(uri=DAMS.check_id, name="check_id", curie=DAMS.curie('check_id'),
                   model_uri=DAMS.check_id, domain=None, range=URIRef)

slots.kind = Slot(uri=DAMS.kind, name="kind", curie=DAMS.curie('kind'),
                   model_uri=DAMS.kind, domain=None, range=Union[str, "FormalCheckKindEnum"])

slots.target_class = Slot(uri=DAMS.target_class, name="target_class", curie=DAMS.curie('target_class'),
                   model_uri=DAMS.target_class, domain=None, range=Optional[str])

slots.target_slot = Slot(uri=DAMS.target_slot, name="target_slot", curie=DAMS.curie('target_slot'),
                   model_uri=DAMS.target_slot, domain=None, range=Optional[str])

slots.target_path = Slot(uri=DAMS.target_path, name="target_path", curie=DAMS.curie('target_path'),
                   model_uri=DAMS.target_path, domain=None, range=Optional[str])

slots.severity = Slot(uri=DAMS.severity, name="severity", curie=DAMS.curie('severity'),
                   model_uri=DAMS.severity, domain=None, range=Union[str, "CheckSeverityEnum"])

slots.diagnostic_code = Slot(uri=DAMS.diagnostic_code, name="diagnostic_code", curie=DAMS.curie('diagnostic_code'),
                   model_uri=DAMS.diagnostic_code, domain=None, range=Optional[str])

slots.expression = Slot(uri=DAMS.expression, name="expression", curie=DAMS.curie('expression'),
                   model_uri=DAMS.expression, domain=None, range=Optional[str])

slots.code = Slot(uri=DAMS.code, name="code", curie=DAMS.curie('code'),
                   model_uri=DAMS.code, domain=None, range=str,
                   pattern=re.compile(r'^(LDM|PDM|REF|ATR|FLW|CLS|GEN)-[0-9]{3}$'))

slots.requirement_level = Slot(uri=DAMS.requirement_level, name="requirement_level", curie=DAMS.curie('requirement_level'),
                   model_uri=DAMS.requirement_level, domain=None, range=Union[str, "RequirementLevelEnum"])

slots.requirement_section = Slot(uri=DAMS.requirement_section, name="requirement_section", curie=DAMS.curie('requirement_section'),
                   model_uri=DAMS.requirement_section, domain=None, range=Union[str, "RequirementSectionEnum"])

slots.statement = Slot(uri=DAMS.statement, name="statement", curie=DAMS.curie('statement'),
                   model_uri=DAMS.statement, domain=None, range=str)

slots.formal_checks = Slot(uri=DAMS.formal_checks, name="formal_checks", curie=DAMS.curie('formal_checks'),
                   model_uri=DAMS.formal_checks, domain=None, range=Optional[Union[dict[Union[str, FormalCheckCheckId], Union[dict, FormalCheck]], list[Union[dict, FormalCheck]]]])

slots.catalog_id = Slot(uri=DAMS.catalog_id, name="catalog_id", curie=DAMS.curie('catalog_id'),
                   model_uri=DAMS.catalog_id, domain=None, range=URIRef)

slots.requirements = Slot(uri=DAMS.requirements, name="requirements", curie=DAMS.curie('requirements'),
                   model_uri=DAMS.requirements, domain=None, range=Optional[Union[dict[Union[str, SpecificationRequirementElementId], Union[dict, SpecificationRequirement]], list[Union[dict, SpecificationRequirement]]]])
