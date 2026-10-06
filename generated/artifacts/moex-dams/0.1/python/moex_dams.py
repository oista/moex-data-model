# Auto generated from moex-dams.yaml by pythongen.py version: 0.0.1
# Generation date: 2026-10-06T20:41:22
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
    PermissibleValue as LinkMLPermissibleValue,
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
version = "2.1.0"

# Namespaces
DAMS = CurieNamespace('dams', 'https://data.moex.com/dams/')
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
MOEX = CurieNamespace('moex', 'https://data.moex.com/')
RDF = CurieNamespace('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
RDFS = CurieNamespace('rdfs', 'http://www.w3.org/2000/01/rdf-schema#')
SKOS = CurieNamespace('skos', 'http://www.w3.org/2004/02/skos/core#')
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


class IdentifiedElementElementId(URIorCURIE):
    pass


class ClassificationAssignmentAssignmentId(URIorCURIE):
    pass


class PolicyBindingPolicyBindingId(URIorCURIE):
    pass


class ScopedDefinitionScopedDefinitionId(URIorCURIE):
    pass


class ModelElementElementId(IdentifiedElementElementId):
    pass


class ModelPackageElementId(ModelElementElementId):
    pass


class DomainContextElementId(ModelElementElementId):
    pass


class ConceptualEntityElementId(ModelElementElementId):
    pass


class ConceptualPropertyElementId(ModelElementElementId):
    pass


class LogicalEntityElementId(ModelElementElementId):
    pass


class LogicalAttributeElementId(ModelElementElementId):
    pass


class RelationshipElementId(ModelElementElementId):
    pass


class RelationTermElementId(ModelElementElementId):
    pass


class ExternalClassRefExternalClassRefId(URIorCURIE):
    pass


class MappingElementId(ModelElementElementId):
    pass


class TechnicalAssetElementId(ModelElementElementId):
    pass


class DataCarrierElementId(TechnicalAssetElementId):
    pass


class AccessPointElementId(TechnicalAssetElementId):
    pass


class DataContainerElementId(TechnicalAssetElementId):
    pass


class ExecutionAssetElementId(TechnicalAssetElementId):
    pass


class ConceptualDomainElementId(ModelElementElementId):
    pass


class ValueMeaningMeaningKey(extended_str):
    pass


class DataTypeElementId(ModelElementElementId):
    pass


class NativeTypeBindingBindingId(URIorCURIE):
    pass


class ValueDomainElementId(ModelElementElementId):
    pass


class PermissibleValueValueCode(extended_str):
    pass


class ValueSetQueryValueSetQueryId(extended_str):
    pass


class EmbeddedElementLocalKey(extended_str):
    pass


class DataStructureElementId(ModelElementElementId):
    pass


class SchemaNodeLocalKey(EmbeddedElementLocalKey):
    pass


class MessageElementId(ModelElementElementId):
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


class RequirementApplicabilityApplicabilityId(extended_str):
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
    Бизнес-домен или предметная область; мастер определяется архитектурным governance
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
class IdentifiedElement(YAMLRoot):
    """
    Элемент с глобальным идентификатором element_id. Не смешивать с EmbeddedElement (local_key). ADR-044.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["IdentifiedElement"]
    class_class_curie: ClassVar[str] = "dams:IdentifiedElement"
    class_name: ClassVar[str] = "IdentifiedElement"
    class_model_uri: ClassVar[URIRef] = DAMS.IdentifiedElement

    element_id: Union[str, IdentifiedElementElementId] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, IdentifiedElementElementId):
            self.element_id = IdentifiedElementElementId(self.element_id)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class NamedElement(YAMLRoot):
    """
    Именование элемента модели (name, title, aliases). ADR-044.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["NamedElement"]
    class_class_curie: ClassVar[str] = "dams:NamedElement"
    class_name: ClassVar[str] = "NamedElement"
    class_model_uri: ClassVar[URIRef] = DAMS.NamedElement

    name: str = None
    title: Optional[str] = None
    aliases: Optional[Union[str, list[str]]] = empty_list()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.name):
            self.MissingRequiredField("name")
        if not isinstance(self.name, str):
            self.name = str(self.name)

        if self.title is not None and not isinstance(self.title, str):
            self.title = str(self.title)

        if not isinstance(self.aliases, list):
            self.aliases = [self.aliases] if self.aliases is not None else []
        self.aliases = [v if isinstance(v, str) else str(v) for v in self.aliases]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class DescribedElement(YAMLRoot):
    """
    Текстовое описание элемента. Глобально не обязательно; обязательность задаётся slot_usage на конкретных классах
    (ADR-044 / ADR-025).
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["DescribedElement"]
    class_class_curie: ClassVar[str] = "dams:DescribedElement"
    class_name: ClassVar[str] = "DescribedElement"
    class_model_uri: ClassVar[URIRef] = DAMS.DescribedElement

    description: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.description is not None and not isinstance(self.description, str):
            self.description = str(self.description)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class HasSemanticAnnotations(YAMLRoot):
    """
    Семантические аннотации (glossary_term_refs, tags). ADR-044.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["HasSemanticAnnotations"]
    class_class_curie: ClassVar[str] = "dams:HasSemanticAnnotations"
    class_name: ClassVar[str] = "HasSemanticAnnotations"
    class_model_uri: ClassVar[URIRef] = DAMS.HasSemanticAnnotations

    glossary_term_refs: Optional[Union[Union[str, GlossaryTermRegistryId], list[Union[str, GlossaryTermRegistryId]]]] = empty_list()
    tags: Optional[Union[str, list[str]]] = empty_list()

    def __post_init__(self, *_: str, **kwargs: Any):
        if not isinstance(self.glossary_term_refs, list):
            self.glossary_term_refs = [self.glossary_term_refs] if self.glossary_term_refs is not None else []
        self.glossary_term_refs = [v if isinstance(v, GlossaryTermRegistryId) else GlossaryTermRegistryId(v) for v in self.glossary_term_refs]

        if not isinstance(self.tags, list):
            self.tags = [self.tags] if self.tags is not None else []
        self.tags = [v if isinstance(v, str) else str(v) for v in self.tags]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class HasValidity(YAMLRoot):
    """
    Период действия элемента (valid_from, valid_to). ADR-044.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["HasValidity"]
    class_class_curie: ClassVar[str] = "dams:HasValidity"
    class_name: ClassVar[str] = "HasValidity"
    class_model_uri: ClassVar[URIRef] = DAMS.HasValidity

    valid_from: Optional[Union[str, XSDDateTime]] = None
    valid_to: Optional[Union[str, XSDDateTime]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.valid_from is not None and not isinstance(self.valid_from, XSDDateTime):
            self.valid_from = XSDDateTime(self.valid_from)

        if self.valid_to is not None and not isinstance(self.valid_to, XSDDateTime):
            self.valid_to = XSDDateTime(self.valid_to)

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
    approval_status: Optional[Union[str, "ApprovalStatusEnum"]] = None
    valid_from: Optional[Union[str, XSDDateTime]] = None
    valid_to: Optional[Union[str, XSDDateTime]] = None

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

        if self.approval_status is not None and not isinstance(self.approval_status, ApprovalStatusEnum):
            self.approval_status = ApprovalStatusEnum(self.approval_status)

        if self.valid_from is not None and not isinstance(self.valid_from, XSDDateTime):
            self.valid_from = XSDDateTime(self.valid_from)

        if self.valid_to is not None and not isinstance(self.valid_to, XSDDateTime):
            self.valid_to = XSDDateTime(self.valid_to)

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
    approval_status: Optional[Union[str, "ApprovalStatusEnum"]] = None
    valid_from: Optional[Union[str, XSDDateTime]] = None
    valid_to: Optional[Union[str, XSDDateTime]] = None

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

        if self.approval_status is not None and not isinstance(self.approval_status, ApprovalStatusEnum):
            self.approval_status = ApprovalStatusEnum(self.approval_status)

        if self.valid_from is not None and not isinstance(self.valid_from, XSDDateTime):
            self.valid_from = XSDDateTime(self.valid_from)

        if self.valid_to is not None and not isinstance(self.valid_to, XSDDateTime):
            self.valid_to = XSDDateTime(self.valid_to)

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
    deprecated_by_ref: Optional[Union[str, URIorCURIE]] = None
    valid_from: Optional[Union[str, XSDDateTime]] = None
    valid_to: Optional[Union[str, XSDDateTime]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.lifecycle_status):
            self.MissingRequiredField("lifecycle_status")
        if not isinstance(self.lifecycle_status, LifecycleStatusEnum):
            self.lifecycle_status = LifecycleStatusEnum(self.lifecycle_status)

        if self.deprecated_by_ref is not None and not isinstance(self.deprecated_by_ref, URIorCURIE):
            self.deprecated_by_ref = URIorCURIE(self.deprecated_by_ref)

        if self.valid_from is not None and not isinstance(self.valid_from, XSDDateTime):
            self.valid_from = XSDDateTime(self.valid_from)

        if self.valid_to is not None and not isinstance(self.valid_to, XSDDateTime):
            self.valid_to = XSDDateTime(self.valid_to)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class HasOwnership(YAMLRoot):
    """
    Mixin владения: data owner, data steward и организационное подразделение. Отсутствие слота означает наследование
    эффективного значения по containment cascade (ADR-023); заданное значение — локальный override.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["HasOwnership"]
    class_class_curie: ClassVar[str] = "dams:HasOwnership"
    class_name: ClassVar[str] = "HasOwnership"
    class_model_uri: ClassVar[URIRef] = DAMS.HasOwnership

    data_owner_ref: Optional[Union[str, RoleRegistryId]] = None
    data_steward_ref: Optional[Union[str, RoleRegistryId]] = None
    owning_unit_ref: Optional[Union[str, OrganizationUnitRegistryId]] = None
    ownership_inheritance_rule: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.data_owner_ref is not None and not isinstance(self.data_owner_ref, RoleRegistryId):
            self.data_owner_ref = RoleRegistryId(self.data_owner_ref)

        if self.data_steward_ref is not None and not isinstance(self.data_steward_ref, RoleRegistryId):
            self.data_steward_ref = RoleRegistryId(self.data_steward_ref)

        if self.owning_unit_ref is not None and not isinstance(self.owning_unit_ref, OrganizationUnitRegistryId):
            self.owning_unit_ref = OrganizationUnitRegistryId(self.owning_unit_ref)

        if self.ownership_inheritance_rule is not None and not isinstance(self.ownership_inheritance_rule, str):
            self.ownership_inheritance_rule = str(self.ownership_inheritance_rule)

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
    Базовая и специальная классификация чувствительности данных. governance_classification участвует в containment
    cascade (ADR-023): пустой слот наследуется от родителя, заданный — override.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["HasGovernanceClassification"]
    class_class_curie: ClassVar[str] = "dams:HasGovernanceClassification"
    class_name: ClassVar[str] = "HasGovernanceClassification"
    class_model_uri: ClassVar[URIRef] = DAMS.HasGovernanceClassification

    governance_classification: Optional[Union[str, "GovernanceClassificationEnum"]] = None
    security_classification: Optional[Union[str, "SecurityClassificationEnum"]] = None
    sensitivity_term_refs: Optional[Union[Union[str, DataClassificationTermRegistryId], list[Union[str, DataClassificationTermRegistryId]]]] = empty_list()
    classification_source: Optional[str] = None
    classification_rationale: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.governance_classification is not None and not isinstance(self.governance_classification, GovernanceClassificationEnum):
            self.governance_classification = GovernanceClassificationEnum(self.governance_classification)

        if self.security_classification is not None and not isinstance(self.security_classification, SecurityClassificationEnum):
            self.security_classification = SecurityClassificationEnum(self.security_classification)

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
    Mixin привязки управляемых политик к элементу модели. policy_refs участвует в containment cascade (ADR-023):
    отсутствие ключа — наследование; присутствующий список (в т.ч. пустой) — полная замена.
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
class HasDefinition(YAMLRoot):
    """
    Mixin эталонного определения (ADR-025 / ADR-044). Слот description индуцируется через DescribedElement;
    exact_mappings указывает skos:definition (slot_uri не меняется — предикат dams:description). Отсутствие
    description при наличии definition_source_ref означает наследование; заданный description — own (опционально
    adapted from source). scoped_definitions — контекстные определения (v1: уровень ITSystem), не заменяющие эталон
    вне scope.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["HasDefinition"]
    class_class_curie: ClassVar[str] = "dams:HasDefinition"
    class_name: ClassVar[str] = "HasDefinition"
    class_model_uri: ClassVar[URIRef] = DAMS.HasDefinition

    definition_source_ref: Optional[Union[str, URIorCURIE]] = None
    definition_rationale: Optional[str] = None
    scoped_definitions: Optional[Union[dict[Union[str, ScopedDefinitionScopedDefinitionId], Union[dict, "ScopedDefinition"]], list[Union[dict, "ScopedDefinition"]]]] = empty_dict()
    description: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.definition_source_ref is not None and not isinstance(self.definition_source_ref, URIorCURIE):
            self.definition_source_ref = URIorCURIE(self.definition_source_ref)

        if self.definition_rationale is not None and not isinstance(self.definition_rationale, str):
            self.definition_rationale = str(self.definition_rationale)

        self._normalize_inlined_as_list(slot_name="scoped_definitions", slot_type=ScopedDefinition, key_name="scoped_definition_id", keyed=True)

        if self.description is not None and not isinstance(self.description, str):
            self.description = str(self.description)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ScopedDefinition(YAMLRoot):
    """
    Контекстное определение элемента модели (ADR-025 / ISO 11179 Context). Не является отдельным термином глоссария и
    не заменяет эталонное определение вне указанного scope.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["ScopedDefinition"]
    class_class_curie: ClassVar[str] = "dams:ScopedDefinition"
    class_name: ClassVar[str] = "ScopedDefinition"
    class_model_uri: ClassVar[URIRef] = DAMS.ScopedDefinition

    scoped_definition_id: Union[str, ScopedDefinitionScopedDefinitionId] = None
    scope_kind: Union[str, "DefinitionScopeKindEnum"] = None
    scope_ref: Union[str, URIorCURIE] = None
    text: str = None
    relation_to_reference: Union[str, "ScopedDefinitionRelationEnum"] = None
    rationale: Optional[str] = None
    source_artifact_ref: Optional[Union[str, URI]] = None
    evidence_refs: Optional[Union[Union[str, URI], list[Union[str, URI]]]] = empty_list()
    approval_status: Optional[Union[str, "ApprovalStatusEnum"]] = None
    approved_by_ref: Optional[Union[str, RoleRegistryId]] = None
    approved_at: Optional[Union[str, XSDDateTime]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.scoped_definition_id):
            self.MissingRequiredField("scoped_definition_id")
        if not isinstance(self.scoped_definition_id, ScopedDefinitionScopedDefinitionId):
            self.scoped_definition_id = ScopedDefinitionScopedDefinitionId(self.scoped_definition_id)

        if self._is_empty(self.scope_kind):
            self.MissingRequiredField("scope_kind")
        if not isinstance(self.scope_kind, DefinitionScopeKindEnum):
            self.scope_kind = DefinitionScopeKindEnum(self.scope_kind)

        if self._is_empty(self.scope_ref):
            self.MissingRequiredField("scope_ref")
        if not isinstance(self.scope_ref, URIorCURIE):
            self.scope_ref = URIorCURIE(self.scope_ref)

        if self._is_empty(self.text):
            self.MissingRequiredField("text")
        if not isinstance(self.text, str):
            self.text = str(self.text)

        if self._is_empty(self.relation_to_reference):
            self.MissingRequiredField("relation_to_reference")
        if not isinstance(self.relation_to_reference, ScopedDefinitionRelationEnum):
            self.relation_to_reference = ScopedDefinitionRelationEnum(self.relation_to_reference)

        if self.rationale is not None and not isinstance(self.rationale, str):
            self.rationale = str(self.rationale)

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
class ModelElement(IdentifiedElement):
    """
    Абстрактный корень именованных элементов модели: IdentifiedElement + NamedElement + DescribedElement +
    HasLifecycle + HasSemanticAnnotations (ADR-044).
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["ModelElement"]
    class_class_curie: ClassVar[str] = "dams:ModelElement"
    class_name: ClassVar[str] = "ModelElement"
    class_model_uri: ClassVar[URIRef] = DAMS.ModelElement

    element_id: Union[str, ModelElementElementId] = None
    name: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    title: Optional[str] = None
    aliases: Optional[Union[str, list[str]]] = empty_list()
    description: Optional[str] = None
    deprecated_by_ref: Optional[Union[str, URIorCURIE]] = None
    glossary_term_refs: Optional[Union[Union[str, GlossaryTermRegistryId], list[Union[str, GlossaryTermRegistryId]]]] = empty_list()
    tags: Optional[Union[str, list[str]]] = empty_list()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.name):
            self.MissingRequiredField("name")
        if not isinstance(self.name, str):
            self.name = str(self.name)

        if self._is_empty(self.lifecycle_status):
            self.MissingRequiredField("lifecycle_status")
        if not isinstance(self.lifecycle_status, LifecycleStatusEnum):
            self.lifecycle_status = LifecycleStatusEnum(self.lifecycle_status)

        if self.title is not None and not isinstance(self.title, str):
            self.title = str(self.title)

        if not isinstance(self.aliases, list):
            self.aliases = [self.aliases] if self.aliases is not None else []
        self.aliases = [v if isinstance(v, str) else str(v) for v in self.aliases]

        if self.description is not None and not isinstance(self.description, str):
            self.description = str(self.description)

        if self.deprecated_by_ref is not None and not isinstance(self.deprecated_by_ref, URIorCURIE):
            self.deprecated_by_ref = URIorCURIE(self.deprecated_by_ref)

        if not isinstance(self.glossary_term_refs, list):
            self.glossary_term_refs = [self.glossary_term_refs] if self.glossary_term_refs is not None else []
        self.glossary_term_refs = [v if isinstance(v, GlossaryTermRegistryId) else GlossaryTermRegistryId(v) for v in self.glossary_term_refs]

        if not isinstance(self.tags, list):
            self.tags = [self.tags] if self.tags is not None else []
        self.tags = [v if isinstance(v, str) else str(v) for v in self.tags]

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
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    api_version: str = None
    model_version: Union[str, SemVer] = None
    description: str = None
    implementation_scope: Optional[Union[str, "ImplementationScopeEnum"]] = None
    conceptual_implementation_ref: Optional[Union[str, URIorCURIE]] = None
    solution_ref: Optional[Union[str, ITSolutionRegistryId]] = None
    domain_refs: Optional[Union[Union[str, BusinessDomainRegistryId], list[Union[str, BusinessDomainRegistryId]]]] = empty_list()
    imports_refs: Optional[Union[Union[str, URI], list[Union[str, URI]]]] = empty_list()
    conceptual_entities: Optional[Union[dict[Union[str, ConceptualEntityElementId], Union[dict, "ConceptualEntity"]], list[Union[dict, "ConceptualEntity"]]]] = empty_dict()
    domain_contexts: Optional[Union[dict[Union[str, DomainContextElementId], Union[dict, "DomainContext"]], list[Union[dict, "DomainContext"]]]] = empty_dict()
    logical_entities: Optional[Union[dict[Union[str, LogicalEntityElementId], Union[dict, "LogicalEntity"]], list[Union[dict, "LogicalEntity"]]]] = empty_dict()
    relationships: Optional[Union[dict[Union[str, RelationshipElementId], Union[dict, "Relationship"]], list[Union[dict, "Relationship"]]]] = empty_dict()
    relation_terms: Optional[Union[dict[Union[str, RelationTermElementId], Union[dict, "RelationTerm"]], list[Union[dict, "RelationTerm"]]]] = empty_dict()
    data_carriers: Optional[Union[dict[Union[str, DataCarrierElementId], Union[dict, "DataCarrier"]], list[Union[dict, "DataCarrier"]]]] = empty_dict()
    access_points: Optional[Union[dict[Union[str, AccessPointElementId], Union[dict, "AccessPoint"]], list[Union[dict, "AccessPoint"]]]] = empty_dict()
    data_containers: Optional[Union[dict[Union[str, DataContainerElementId], Union[dict, "DataContainer"]], list[Union[dict, "DataContainer"]]]] = empty_dict()
    execution_assets: Optional[Union[dict[Union[str, ExecutionAssetElementId], Union[dict, "ExecutionAsset"]], list[Union[dict, "ExecutionAsset"]]]] = empty_dict()
    mappings: Optional[Union[dict[Union[str, MappingElementId], Union[dict, "Mapping"]], list[Union[dict, "Mapping"]]]] = empty_dict()
    conceptual_properties: Optional[Union[dict[Union[str, ConceptualPropertyElementId], Union[dict, "ConceptualProperty"]], list[Union[dict, "ConceptualProperty"]]]] = empty_dict()
    conceptual_domains: Optional[Union[dict[Union[str, ConceptualDomainElementId], Union[dict, "ConceptualDomain"]], list[Union[dict, "ConceptualDomain"]]]] = empty_dict()
    value_domains: Optional[Union[dict[Union[str, ValueDomainElementId], Union[dict, "ValueDomain"]], list[Union[dict, "ValueDomain"]]]] = empty_dict()
    data_types: Optional[Union[dict[Union[str, DataTypeElementId], Union[dict, "DataType"]], list[Union[dict, "DataType"]]]] = empty_dict()
    native_type_bindings: Optional[Union[dict[Union[str, NativeTypeBindingBindingId], Union[dict, "NativeTypeBinding"]], list[Union[dict, "NativeTypeBinding"]]]] = empty_dict()
    data_structures: Optional[Union[dict[Union[str, DataStructureElementId], Union[dict, "DataStructure"]], list[Union[dict, "DataStructure"]]]] = empty_dict()
    messages: Optional[Union[dict[Union[str, MessageElementId], Union[dict, "Message"]], list[Union[dict, "Message"]]]] = empty_dict()
    data_owner_ref: Optional[Union[str, RoleRegistryId]] = None
    data_steward_ref: Optional[Union[str, RoleRegistryId]] = None
    owning_unit_ref: Optional[Union[str, OrganizationUnitRegistryId]] = None
    ownership_inheritance_rule: Optional[str] = None
    governance_classification: Optional[Union[str, "GovernanceClassificationEnum"]] = None
    security_classification: Optional[Union[str, "SecurityClassificationEnum"]] = None
    sensitivity_term_refs: Optional[Union[Union[str, DataClassificationTermRegistryId], list[Union[str, DataClassificationTermRegistryId]]]] = empty_list()
    classification_source: Optional[str] = None
    classification_rationale: Optional[str] = None
    policy_refs: Optional[Union[Union[str, PolicyRegistryId], list[Union[str, PolicyRegistryId]]]] = empty_list()

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

        if self._is_empty(self.description):
            self.MissingRequiredField("description")
        if not isinstance(self.description, str):
            self.description = str(self.description)

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

        self._normalize_inlined_as_list(slot_name="relation_terms", slot_type=RelationTerm, key_name="element_id", keyed=True)

        self._normalize_inlined_as_list(slot_name="data_carriers", slot_type=DataCarrier, key_name="element_id", keyed=True)

        self._normalize_inlined_as_list(slot_name="access_points", slot_type=AccessPoint, key_name="element_id", keyed=True)

        self._normalize_inlined_as_list(slot_name="data_containers", slot_type=DataContainer, key_name="element_id", keyed=True)

        self._normalize_inlined_as_list(slot_name="execution_assets", slot_type=ExecutionAsset, key_name="element_id", keyed=True)

        self._normalize_inlined_as_list(slot_name="mappings", slot_type=Mapping, key_name="element_id", keyed=True)

        self._normalize_inlined_as_list(slot_name="conceptual_properties", slot_type=ConceptualProperty, key_name="element_id", keyed=True)

        self._normalize_inlined_as_list(slot_name="conceptual_domains", slot_type=ConceptualDomain, key_name="element_id", keyed=True)

        self._normalize_inlined_as_list(slot_name="value_domains", slot_type=ValueDomain, key_name="element_id", keyed=True)

        self._normalize_inlined_as_list(slot_name="data_types", slot_type=DataType, key_name="element_id", keyed=True)

        self._normalize_inlined_as_list(slot_name="native_type_bindings", slot_type=NativeTypeBinding, key_name="binding_id", keyed=True)

        self._normalize_inlined_as_list(slot_name="data_structures", slot_type=DataStructure, key_name="element_id", keyed=True)

        self._normalize_inlined_as_list(slot_name="messages", slot_type=Message, key_name="element_id", keyed=True)

        if self.data_owner_ref is not None and not isinstance(self.data_owner_ref, RoleRegistryId):
            self.data_owner_ref = RoleRegistryId(self.data_owner_ref)

        if self.data_steward_ref is not None and not isinstance(self.data_steward_ref, RoleRegistryId):
            self.data_steward_ref = RoleRegistryId(self.data_steward_ref)

        if self.owning_unit_ref is not None and not isinstance(self.owning_unit_ref, OrganizationUnitRegistryId):
            self.owning_unit_ref = OrganizationUnitRegistryId(self.owning_unit_ref)

        if self.ownership_inheritance_rule is not None and not isinstance(self.ownership_inheritance_rule, str):
            self.ownership_inheritance_rule = str(self.ownership_inheritance_rule)

        if self.governance_classification is not None and not isinstance(self.governance_classification, GovernanceClassificationEnum):
            self.governance_classification = GovernanceClassificationEnum(self.governance_classification)

        if self.security_classification is not None and not isinstance(self.security_classification, SecurityClassificationEnum):
            self.security_classification = SecurityClassificationEnum(self.security_classification)

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
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    domain_ref: Union[str, BusinessDomainRegistryId] = None
    namespace: Union[str, URI] = None
    description: str = None
    solution_ref: Optional[Union[str, ITSolutionRegistryId]] = None
    business_process_refs: Optional[Union[Union[str, BusinessProcessRegistryId], list[Union[str, BusinessProcessRegistryId]]]] = empty_list()
    data_owner_ref: Optional[Union[str, RoleRegistryId]] = None
    data_steward_ref: Optional[Union[str, RoleRegistryId]] = None
    owning_unit_ref: Optional[Union[str, OrganizationUnitRegistryId]] = None
    ownership_inheritance_rule: Optional[str] = None

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

        if self._is_empty(self.description):
            self.MissingRequiredField("description")
        if not isinstance(self.description, str):
            self.description = str(self.description)

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

        if self.ownership_inheritance_rule is not None and not isinstance(self.ownership_inheritance_rule, str):
            self.ownership_inheritance_rule = str(self.ownership_inheritance_rule)

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
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    parent_concept_ref: Optional[Union[str, ConceptualEntityElementId]] = None
    key_attribute_refs: Optional[Union[Union[str, URIorCURIE], list[Union[str, URIorCURIE]]]] = empty_list()
    entity_tier: Optional[Union[str, "EntityTierEnum"]] = None
    dependency_kind: Optional[Union[str, "DependencyKindEnum"]] = None
    depends_on_refs: Optional[Union[Union[str, ConceptualEntityElementId], list[Union[str, ConceptualEntityElementId]]]] = empty_list()
    genesis_kind: Optional[Union[str, "GenesisKindEnum"]] = None
    external_class_refs: Optional[Union[dict[Union[str, ExternalClassRefExternalClassRefId], Union[dict, "ExternalClassRef"]], list[Union[dict, "ExternalClassRef"]]]] = empty_dict()
    data_owner_ref: Optional[Union[str, RoleRegistryId]] = None
    data_steward_ref: Optional[Union[str, RoleRegistryId]] = None
    owning_unit_ref: Optional[Union[str, OrganizationUnitRegistryId]] = None
    ownership_inheritance_rule: Optional[str] = None
    entity_type: Optional[Union[str, "EntityTypeEnum"]] = None
    data_class: Optional[Union[str, "DataClassEnum"]] = None
    business_importance: Optional[Union[str, "BusinessImportanceEnum"]] = None
    definition_source_ref: Optional[Union[str, URIorCURIE]] = None
    definition_rationale: Optional[str] = None
    scoped_definitions: Optional[Union[dict[Union[str, ScopedDefinitionScopedDefinitionId], Union[dict, ScopedDefinition]], list[Union[dict, ScopedDefinition]]]] = empty_dict()

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

        if self.entity_tier is not None and not isinstance(self.entity_tier, EntityTierEnum):
            self.entity_tier = EntityTierEnum(self.entity_tier)

        if self.dependency_kind is not None and not isinstance(self.dependency_kind, DependencyKindEnum):
            self.dependency_kind = DependencyKindEnum(self.dependency_kind)

        if not isinstance(self.depends_on_refs, list):
            self.depends_on_refs = [self.depends_on_refs] if self.depends_on_refs is not None else []
        self.depends_on_refs = [v if isinstance(v, ConceptualEntityElementId) else ConceptualEntityElementId(v) for v in self.depends_on_refs]

        if self.genesis_kind is not None and not isinstance(self.genesis_kind, GenesisKindEnum):
            self.genesis_kind = GenesisKindEnum(self.genesis_kind)

        self._normalize_inlined_as_list(slot_name="external_class_refs", slot_type=ExternalClassRef, key_name="external_class_ref_id", keyed=True)

        if self.data_owner_ref is not None and not isinstance(self.data_owner_ref, RoleRegistryId):
            self.data_owner_ref = RoleRegistryId(self.data_owner_ref)

        if self.data_steward_ref is not None and not isinstance(self.data_steward_ref, RoleRegistryId):
            self.data_steward_ref = RoleRegistryId(self.data_steward_ref)

        if self.owning_unit_ref is not None and not isinstance(self.owning_unit_ref, OrganizationUnitRegistryId):
            self.owning_unit_ref = OrganizationUnitRegistryId(self.owning_unit_ref)

        if self.ownership_inheritance_rule is not None and not isinstance(self.ownership_inheritance_rule, str):
            self.ownership_inheritance_rule = str(self.ownership_inheritance_rule)

        if self.entity_type is not None and not isinstance(self.entity_type, EntityTypeEnum):
            self.entity_type = EntityTypeEnum(self.entity_type)

        if self.data_class is not None and not isinstance(self.data_class, DataClassEnum):
            self.data_class = DataClassEnum(self.data_class)

        if self.business_importance is not None and not isinstance(self.business_importance, BusinessImportanceEnum):
            self.business_importance = BusinessImportanceEnum(self.business_importance)

        if self.definition_source_ref is not None and not isinstance(self.definition_source_ref, URIorCURIE):
            self.definition_source_ref = URIorCURIE(self.definition_source_ref)

        if self.definition_rationale is not None and not isinstance(self.definition_rationale, str):
            self.definition_rationale = str(self.definition_rationale)

        self._normalize_inlined_as_list(slot_name="scoped_definitions", slot_type=ScopedDefinition, key_name="scoped_definition_id", keyed=True)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ConceptualProperty(ModelElement):
    """
    Значимое концептуальное свойство сущности КМД. Создаётся только при наличии significance_basis; не обязательно для
    каждого LogicalAttribute.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["ConceptualProperty"]
    class_class_curie: ClassVar[str] = "dams:ConceptualProperty"
    class_name: ClassVar[str] = "ConceptualProperty"
    class_model_uri: ClassVar[URIRef] = DAMS.ConceptualProperty

    element_id: Union[str, ConceptualPropertyElementId] = None
    name: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    property_owner_entity_ref: Union[str, ConceptualEntityElementId] = None
    significance_basis: Union[Union[str, "SignificanceBasisEnum"], list[Union[str, "SignificanceBasisEnum"]]] = None
    property_kind: Union[str, "PropertyKindEnum"] = None
    genesis_kind: Union[str, "GenesisKindEnum"] = None
    significance_rationale: Optional[str] = None
    conceptual_domain_ref: Optional[Union[str, ConceptualDomainElementId]] = None
    is_identifying: Optional[Union[bool, Bool]] = None
    data_owner_ref: Optional[Union[str, RoleRegistryId]] = None
    data_steward_ref: Optional[Union[str, RoleRegistryId]] = None
    owning_unit_ref: Optional[Union[str, OrganizationUnitRegistryId]] = None
    ownership_inheritance_rule: Optional[str] = None
    definition_source_ref: Optional[Union[str, URIorCURIE]] = None
    definition_rationale: Optional[str] = None
    scoped_definitions: Optional[Union[dict[Union[str, ScopedDefinitionScopedDefinitionId], Union[dict, ScopedDefinition]], list[Union[dict, ScopedDefinition]]]] = empty_dict()
    source_artifact_ref: Optional[Union[str, URI]] = None
    evidence_refs: Optional[Union[Union[str, URI], list[Union[str, URI]]]] = empty_list()
    approval_status: Optional[Union[str, "ApprovalStatusEnum"]] = None
    approved_by_ref: Optional[Union[str, RoleRegistryId]] = None
    approved_at: Optional[Union[str, XSDDateTime]] = None
    policy_refs: Optional[Union[Union[str, PolicyRegistryId], list[Union[str, PolicyRegistryId]]]] = empty_list()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, ConceptualPropertyElementId):
            self.element_id = ConceptualPropertyElementId(self.element_id)

        if self._is_empty(self.property_owner_entity_ref):
            self.MissingRequiredField("property_owner_entity_ref")
        if not isinstance(self.property_owner_entity_ref, ConceptualEntityElementId):
            self.property_owner_entity_ref = ConceptualEntityElementId(self.property_owner_entity_ref)

        if self._is_empty(self.significance_basis):
            self.MissingRequiredField("significance_basis")
        if not isinstance(self.significance_basis, list):
            self.significance_basis = [self.significance_basis] if self.significance_basis is not None else []
        self.significance_basis = [v if isinstance(v, SignificanceBasisEnum) else SignificanceBasisEnum(v) for v in self.significance_basis]

        if self._is_empty(self.property_kind):
            self.MissingRequiredField("property_kind")
        if not isinstance(self.property_kind, PropertyKindEnum):
            self.property_kind = PropertyKindEnum(self.property_kind)

        if self._is_empty(self.genesis_kind):
            self.MissingRequiredField("genesis_kind")
        if not isinstance(self.genesis_kind, GenesisKindEnum):
            self.genesis_kind = GenesisKindEnum(self.genesis_kind)

        if self.significance_rationale is not None and not isinstance(self.significance_rationale, str):
            self.significance_rationale = str(self.significance_rationale)

        if self.conceptual_domain_ref is not None and not isinstance(self.conceptual_domain_ref, ConceptualDomainElementId):
            self.conceptual_domain_ref = ConceptualDomainElementId(self.conceptual_domain_ref)

        if self.is_identifying is not None and not isinstance(self.is_identifying, Bool):
            self.is_identifying = Bool(self.is_identifying)

        if self.data_owner_ref is not None and not isinstance(self.data_owner_ref, RoleRegistryId):
            self.data_owner_ref = RoleRegistryId(self.data_owner_ref)

        if self.data_steward_ref is not None and not isinstance(self.data_steward_ref, RoleRegistryId):
            self.data_steward_ref = RoleRegistryId(self.data_steward_ref)

        if self.owning_unit_ref is not None and not isinstance(self.owning_unit_ref, OrganizationUnitRegistryId):
            self.owning_unit_ref = OrganizationUnitRegistryId(self.owning_unit_ref)

        if self.ownership_inheritance_rule is not None and not isinstance(self.ownership_inheritance_rule, str):
            self.ownership_inheritance_rule = str(self.ownership_inheritance_rule)

        if self.definition_source_ref is not None and not isinstance(self.definition_source_ref, URIorCURIE):
            self.definition_source_ref = URIorCURIE(self.definition_source_ref)

        if self.definition_rationale is not None and not isinstance(self.definition_rationale, str):
            self.definition_rationale = str(self.definition_rationale)

        self._normalize_inlined_as_list(slot_name="scoped_definitions", slot_type=ScopedDefinition, key_name="scoped_definition_id", keyed=True)

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

        if not isinstance(self.policy_refs, list):
            self.policy_refs = [self.policy_refs] if self.policy_refs is not None else []
        self.policy_refs = [v if isinstance(v, PolicyRegistryId) else PolicyRegistryId(v) for v in self.policy_refs]

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
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    context_ref: Union[str, DomainContextElementId] = None
    solution_data_role: Union[str, "SolutionDataRoleEnum"] = None
    conceptual_entity_refs: Optional[Union[Union[str, ConceptualEntityElementId], list[Union[str, ConceptualEntityElementId]]]] = empty_list()
    solution_ref: Optional[Union[str, ITSolutionRegistryId]] = None
    attributes: Optional[Union[dict[Union[str, LogicalAttributeElementId], Union[dict, "LogicalAttribute"]], list[Union[dict, "LogicalAttribute"]]]] = empty_dict()
    key_attribute_refs: Optional[Union[Union[str, URIorCURIE], list[Union[str, URIorCURIE]]]] = empty_list()
    invariant_refs: Optional[Union[Union[str, PolicyRegistryId], list[Union[str, PolicyRegistryId]]]] = empty_list()
    identity_rule: Optional[str] = None
    business_key_kind: Optional[Union[str, "BusinessKeyKindEnum"]] = None
    conceptual_alignment_status: Optional[Union[str, "ConceptualAlignmentStatusEnum"]] = None
    alignment_rationale: Optional[str] = None
    isolation_rationale: Optional[str] = None
    data_owner_ref: Optional[Union[str, RoleRegistryId]] = None
    data_steward_ref: Optional[Union[str, RoleRegistryId]] = None
    owning_unit_ref: Optional[Union[str, OrganizationUnitRegistryId]] = None
    ownership_inheritance_rule: Optional[str] = None
    entity_type: Optional[Union[str, "EntityTypeEnum"]] = None
    data_class: Optional[Union[str, "DataClassEnum"]] = None
    business_importance: Optional[Union[str, "BusinessImportanceEnum"]] = None
    governance_classification: Optional[Union[str, "GovernanceClassificationEnum"]] = None
    security_classification: Optional[Union[str, "SecurityClassificationEnum"]] = None
    sensitivity_term_refs: Optional[Union[Union[str, DataClassificationTermRegistryId], list[Union[str, DataClassificationTermRegistryId]]]] = empty_list()
    classification_source: Optional[str] = None
    classification_rationale: Optional[str] = None
    policy_refs: Optional[Union[Union[str, PolicyRegistryId], list[Union[str, PolicyRegistryId]]]] = empty_list()
    definition_source_ref: Optional[Union[str, URIorCURIE]] = None
    definition_rationale: Optional[str] = None
    scoped_definitions: Optional[Union[dict[Union[str, ScopedDefinitionScopedDefinitionId], Union[dict, ScopedDefinition]], list[Union[dict, ScopedDefinition]]]] = empty_dict()

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

        if self.identity_rule is not None and not isinstance(self.identity_rule, str):
            self.identity_rule = str(self.identity_rule)

        if self.business_key_kind is not None and not isinstance(self.business_key_kind, BusinessKeyKindEnum):
            self.business_key_kind = BusinessKeyKindEnum(self.business_key_kind)

        if self.conceptual_alignment_status is not None and not isinstance(self.conceptual_alignment_status, ConceptualAlignmentStatusEnum):
            self.conceptual_alignment_status = ConceptualAlignmentStatusEnum(self.conceptual_alignment_status)

        if self.alignment_rationale is not None and not isinstance(self.alignment_rationale, str):
            self.alignment_rationale = str(self.alignment_rationale)

        if self.isolation_rationale is not None and not isinstance(self.isolation_rationale, str):
            self.isolation_rationale = str(self.isolation_rationale)

        if self.data_owner_ref is not None and not isinstance(self.data_owner_ref, RoleRegistryId):
            self.data_owner_ref = RoleRegistryId(self.data_owner_ref)

        if self.data_steward_ref is not None and not isinstance(self.data_steward_ref, RoleRegistryId):
            self.data_steward_ref = RoleRegistryId(self.data_steward_ref)

        if self.owning_unit_ref is not None and not isinstance(self.owning_unit_ref, OrganizationUnitRegistryId):
            self.owning_unit_ref = OrganizationUnitRegistryId(self.owning_unit_ref)

        if self.ownership_inheritance_rule is not None and not isinstance(self.ownership_inheritance_rule, str):
            self.ownership_inheritance_rule = str(self.ownership_inheritance_rule)

        if self.entity_type is not None and not isinstance(self.entity_type, EntityTypeEnum):
            self.entity_type = EntityTypeEnum(self.entity_type)

        if self.data_class is not None and not isinstance(self.data_class, DataClassEnum):
            self.data_class = DataClassEnum(self.data_class)

        if self.business_importance is not None and not isinstance(self.business_importance, BusinessImportanceEnum):
            self.business_importance = BusinessImportanceEnum(self.business_importance)

        if self.governance_classification is not None and not isinstance(self.governance_classification, GovernanceClassificationEnum):
            self.governance_classification = GovernanceClassificationEnum(self.governance_classification)

        if self.security_classification is not None and not isinstance(self.security_classification, SecurityClassificationEnum):
            self.security_classification = SecurityClassificationEnum(self.security_classification)

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

        if self.definition_source_ref is not None and not isinstance(self.definition_source_ref, URIorCURIE):
            self.definition_source_ref = URIorCURIE(self.definition_source_ref)

        if self.definition_rationale is not None and not isinstance(self.definition_rationale, str):
            self.definition_rationale = str(self.definition_rationale)

        self._normalize_inlined_as_list(slot_name="scoped_definitions", slot_type=ScopedDefinition, key_name="scoped_definition_id", keyed=True)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class LogicalAttribute(ModelElement):
    """
    Логический атрибут сущности: идентификация, обязательность, кардинальность и ссылки на представление
    (DataType/ValueDomain) и опционально на ConceptualProperty (вариант B, ADR-034).
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["LogicalAttribute"]
    class_class_curie: ClassVar[str] = "dams:LogicalAttribute"
    class_name: ClassVar[str] = "LogicalAttribute"
    class_model_uri: ClassVar[URIRef] = DAMS.LogicalAttribute

    element_id: Union[str, LogicalAttributeElementId] = None
    name: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    owner_entity_ref: Union[str, LogicalEntityElementId] = None
    required: Union[bool, Bool] = None
    multivalued: Union[bool, Bool] = None
    concept_ref: Optional[Union[str, ConceptualPropertyElementId]] = None
    value_domain_ref: Optional[Union[str, ValueDomainElementId]] = None
    data_type_ref: Optional[Union[str, DataTypeElementId]] = None
    critical_data_element: Optional[Union[bool, Bool]] = None
    minimum_cardinality: Optional[int] = None
    maximum_cardinality: Optional[int] = None
    default_value: Optional[str] = None
    derived_expression: Optional[str] = None
    mapping_coverage_status: Optional[Union[str, "MappingCoverageStatusEnum"]] = None
    mapping_rationale: Optional[str] = None
    currency_attribute_ref: Optional[Union[str, URIorCURIE]] = None
    timezone_policy: Optional[str] = None
    temporal_semantics: Optional[str] = None
    data_owner_ref: Optional[Union[str, RoleRegistryId]] = None
    data_steward_ref: Optional[Union[str, RoleRegistryId]] = None
    owning_unit_ref: Optional[Union[str, OrganizationUnitRegistryId]] = None
    ownership_inheritance_rule: Optional[str] = None
    governance_classification: Optional[Union[str, "GovernanceClassificationEnum"]] = None
    security_classification: Optional[Union[str, "SecurityClassificationEnum"]] = None
    sensitivity_term_refs: Optional[Union[Union[str, DataClassificationTermRegistryId], list[Union[str, DataClassificationTermRegistryId]]]] = empty_list()
    classification_source: Optional[str] = None
    classification_rationale: Optional[str] = None
    policy_refs: Optional[Union[Union[str, PolicyRegistryId], list[Union[str, PolicyRegistryId]]]] = empty_list()
    definition_source_ref: Optional[Union[str, URIorCURIE]] = None
    definition_rationale: Optional[str] = None
    scoped_definitions: Optional[Union[dict[Union[str, ScopedDefinitionScopedDefinitionId], Union[dict, ScopedDefinition]], list[Union[dict, ScopedDefinition]]]] = empty_dict()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, LogicalAttributeElementId):
            self.element_id = LogicalAttributeElementId(self.element_id)

        if self._is_empty(self.owner_entity_ref):
            self.MissingRequiredField("owner_entity_ref")
        if not isinstance(self.owner_entity_ref, LogicalEntityElementId):
            self.owner_entity_ref = LogicalEntityElementId(self.owner_entity_ref)

        if self._is_empty(self.required):
            self.MissingRequiredField("required")
        if not isinstance(self.required, Bool):
            self.required = Bool(self.required)

        if self._is_empty(self.multivalued):
            self.MissingRequiredField("multivalued")
        if not isinstance(self.multivalued, Bool):
            self.multivalued = Bool(self.multivalued)

        if self.concept_ref is not None and not isinstance(self.concept_ref, ConceptualPropertyElementId):
            self.concept_ref = ConceptualPropertyElementId(self.concept_ref)

        if self.value_domain_ref is not None and not isinstance(self.value_domain_ref, ValueDomainElementId):
            self.value_domain_ref = ValueDomainElementId(self.value_domain_ref)

        if self.data_type_ref is not None and not isinstance(self.data_type_ref, DataTypeElementId):
            self.data_type_ref = DataTypeElementId(self.data_type_ref)

        if self.critical_data_element is not None and not isinstance(self.critical_data_element, Bool):
            self.critical_data_element = Bool(self.critical_data_element)

        if self.minimum_cardinality is not None and not isinstance(self.minimum_cardinality, int):
            self.minimum_cardinality = int(self.minimum_cardinality)

        if self.maximum_cardinality is not None and not isinstance(self.maximum_cardinality, int):
            self.maximum_cardinality = int(self.maximum_cardinality)

        if self.default_value is not None and not isinstance(self.default_value, str):
            self.default_value = str(self.default_value)

        if self.derived_expression is not None and not isinstance(self.derived_expression, str):
            self.derived_expression = str(self.derived_expression)

        if self.mapping_coverage_status is not None and not isinstance(self.mapping_coverage_status, MappingCoverageStatusEnum):
            self.mapping_coverage_status = MappingCoverageStatusEnum(self.mapping_coverage_status)

        if self.mapping_rationale is not None and not isinstance(self.mapping_rationale, str):
            self.mapping_rationale = str(self.mapping_rationale)

        if self.currency_attribute_ref is not None and not isinstance(self.currency_attribute_ref, URIorCURIE):
            self.currency_attribute_ref = URIorCURIE(self.currency_attribute_ref)

        if self.timezone_policy is not None and not isinstance(self.timezone_policy, str):
            self.timezone_policy = str(self.timezone_policy)

        if self.temporal_semantics is not None and not isinstance(self.temporal_semantics, str):
            self.temporal_semantics = str(self.temporal_semantics)

        if self.data_owner_ref is not None and not isinstance(self.data_owner_ref, RoleRegistryId):
            self.data_owner_ref = RoleRegistryId(self.data_owner_ref)

        if self.data_steward_ref is not None and not isinstance(self.data_steward_ref, RoleRegistryId):
            self.data_steward_ref = RoleRegistryId(self.data_steward_ref)

        if self.owning_unit_ref is not None and not isinstance(self.owning_unit_ref, OrganizationUnitRegistryId):
            self.owning_unit_ref = OrganizationUnitRegistryId(self.owning_unit_ref)

        if self.ownership_inheritance_rule is not None and not isinstance(self.ownership_inheritance_rule, str):
            self.ownership_inheritance_rule = str(self.ownership_inheritance_rule)

        if self.governance_classification is not None and not isinstance(self.governance_classification, GovernanceClassificationEnum):
            self.governance_classification = GovernanceClassificationEnum(self.governance_classification)

        if self.security_classification is not None and not isinstance(self.security_classification, SecurityClassificationEnum):
            self.security_classification = SecurityClassificationEnum(self.security_classification)

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

        if self.definition_source_ref is not None and not isinstance(self.definition_source_ref, URIorCURIE):
            self.definition_source_ref = URIorCURIE(self.definition_source_ref)

        if self.definition_rationale is not None and not isinstance(self.definition_rationale, str):
            self.definition_rationale = str(self.definition_rationale)

        self._normalize_inlined_as_list(slot_name="scoped_definitions", slot_type=ScopedDefinition, key_name="scoped_definition_id", keyed=True)

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
    relationship_kind: Optional[Union[str, "RelationshipKindEnum"]] = None
    cardinality_rationale: Optional[str] = None
    relation_term_ref: Optional[Union[str, RelationTermElementId]] = None
    term_direction: Optional[Union[str, "TermDirectionEnum"]] = None

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

        if self.relationship_kind is not None and not isinstance(self.relationship_kind, RelationshipKindEnum):
            self.relationship_kind = RelationshipKindEnum(self.relationship_kind)

        if self.cardinality_rationale is not None and not isinstance(self.cardinality_rationale, str):
            self.cardinality_rationale = str(self.cardinality_rationale)

        if self.relation_term_ref is not None and not isinstance(self.relation_term_ref, RelationTermElementId):
            self.relation_term_ref = RelationTermElementId(self.relation_term_ref)

        if self.term_direction is not None and not isinstance(self.term_direction, TermDirectionEnum):
            self.term_direction = TermDirectionEnum(self.term_direction)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class RelationTerm(ModelElement):
    """
    Governed dictionary term for a conceptual/logical relationship (ADR-026). Provides forward and inverse
    natural-language labels so a single Relationship assertion can be read from either side.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["RelationTerm"]
    class_class_curie: ClassVar[str] = "dams:RelationTerm"
    class_name: ClassVar[str] = "RelationTerm"
    class_model_uri: ClassVar[URIRef] = DAMS.RelationTerm

    element_id: Union[str, RelationTermElementId] = None
    name: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    forward_label: str = None
    forward_label_en: Optional[str] = None
    inverse_label: Optional[str] = None
    inverse_label_en: Optional[str] = None
    symmetric: Optional[Union[bool, Bool]] = None
    default_relationship_kind: Optional[Union[str, "RelationshipKindEnum"]] = None
    ontology_property_ref: Optional[Union[str, URIorCURIE]] = None
    definition_source_ref: Optional[Union[str, URIorCURIE]] = None
    definition_rationale: Optional[str] = None
    scoped_definitions: Optional[Union[dict[Union[str, ScopedDefinitionScopedDefinitionId], Union[dict, ScopedDefinition]], list[Union[dict, ScopedDefinition]]]] = empty_dict()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, RelationTermElementId):
            self.element_id = RelationTermElementId(self.element_id)

        if self._is_empty(self.forward_label):
            self.MissingRequiredField("forward_label")
        if not isinstance(self.forward_label, str):
            self.forward_label = str(self.forward_label)

        if self.forward_label_en is not None and not isinstance(self.forward_label_en, str):
            self.forward_label_en = str(self.forward_label_en)

        if self.inverse_label is not None and not isinstance(self.inverse_label, str):
            self.inverse_label = str(self.inverse_label)

        if self.inverse_label_en is not None and not isinstance(self.inverse_label_en, str):
            self.inverse_label_en = str(self.inverse_label_en)

        if self.symmetric is not None and not isinstance(self.symmetric, Bool):
            self.symmetric = Bool(self.symmetric)

        if self.default_relationship_kind is not None and not isinstance(self.default_relationship_kind, RelationshipKindEnum):
            self.default_relationship_kind = RelationshipKindEnum(self.default_relationship_kind)

        if self.ontology_property_ref is not None and not isinstance(self.ontology_property_ref, URIorCURIE):
            self.ontology_property_ref = URIorCURIE(self.ontology_property_ref)

        if self.definition_source_ref is not None and not isinstance(self.definition_source_ref, URIorCURIE):
            self.definition_source_ref = URIorCURIE(self.definition_source_ref)

        if self.definition_rationale is not None and not isinstance(self.definition_rationale, str):
            self.definition_rationale = str(self.definition_rationale)

        self._normalize_inlined_as_list(slot_name="scoped_definitions", slot_type=ScopedDefinition, key_name="scoped_definition_id", keyed=True)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ExternalClassRef(YAMLRoot):
    """
    Alignment of a ConceptualEntity to an external class or term (ADR-026). Canonical store for conceptual↔external
    links; Mapping(aligns_with) may mirror for ExternalTermSelection projections.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["ExternalClassRef"]
    class_class_curie: ClassVar[str] = "dams:ExternalClassRef"
    class_name: ClassVar[str] = "ExternalClassRef"
    class_model_uri: ClassVar[URIRef] = DAMS.ExternalClassRef

    external_class_ref_id: Union[str, ExternalClassRefExternalClassRefId] = None
    target_ref: Union[str, URIorCURIE] = None
    match_kind: Union[str, "ExternalMatchKindEnum"] = None
    source_kind: Union[str, "ExternalSourceKindEnum"] = None
    external_specification_ref: Optional[Union[str, URIorCURIE]] = None
    selection_ref: Optional[Union[str, URIorCURIE]] = None
    source_artifact_ref: Optional[Union[str, URI]] = None
    evidence_refs: Optional[Union[Union[str, URI], list[Union[str, URI]]]] = empty_list()
    approval_status: Optional[Union[str, "ApprovalStatusEnum"]] = None
    approved_by_ref: Optional[Union[str, RoleRegistryId]] = None
    approved_at: Optional[Union[str, XSDDateTime]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.external_class_ref_id):
            self.MissingRequiredField("external_class_ref_id")
        if not isinstance(self.external_class_ref_id, ExternalClassRefExternalClassRefId):
            self.external_class_ref_id = ExternalClassRefExternalClassRefId(self.external_class_ref_id)

        if self._is_empty(self.target_ref):
            self.MissingRequiredField("target_ref")
        if not isinstance(self.target_ref, URIorCURIE):
            self.target_ref = URIorCURIE(self.target_ref)

        if self._is_empty(self.match_kind):
            self.MissingRequiredField("match_kind")
        if not isinstance(self.match_kind, ExternalMatchKindEnum):
            self.match_kind = ExternalMatchKindEnum(self.match_kind)

        if self._is_empty(self.source_kind):
            self.MissingRequiredField("source_kind")
        if not isinstance(self.source_kind, ExternalSourceKindEnum):
            self.source_kind = ExternalSourceKindEnum(self.source_kind)

        if self.external_specification_ref is not None and not isinstance(self.external_specification_ref, URIorCURIE):
            self.external_specification_ref = URIorCURIE(self.external_specification_ref)

        if self.selection_ref is not None and not isinstance(self.selection_ref, URIorCURIE):
            self.selection_ref = URIorCURIE(self.selection_ref)

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
class Mapping(ModelElement):
    """
    Явное соответствие между элементами. Discriminate via mapping_type: realizes (solution→enterprise conceptual),
    entity_physical (DataCarrier↔LogicalEntity), field_mapping/mapsTo (SchemaNode↔LogicalAttribute), aligns_with
    (enterprise↔external term). Not used for SpecImpl implements/conforms_to.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["Mapping"]
    class_class_curie: ClassVar[str] = "dams:Mapping"
    class_name: ClassVar[str] = "Mapping"
    class_model_uri: ClassVar[URIRef] = DAMS.Mapping

    element_id: Union[str, MappingElementId] = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    mapping_type: Union[str, "MappingTypeEnum"] = None
    mapping_cardinality: Union[str, "MappingCardinalityEnum"] = None
    name: str = None
    source_refs: Optional[Union[Union[str, URIorCURIE], list[Union[str, URIorCURIE]]]] = empty_list()
    target_refs: Optional[Union[Union[str, URIorCURIE], list[Union[str, URIorCURIE]]]] = empty_list()
    transformation_ref: Optional[Union[str, URI]] = None
    transformation_expression: Optional[str] = None
    confidence: Optional[Decimal] = None
    title: Optional[str] = None
    aliases: Optional[Union[str, list[str]]] = empty_list()
    glossary_term_refs: Optional[Union[Union[str, GlossaryTermRegistryId], list[Union[str, GlossaryTermRegistryId]]]] = empty_list()
    tags: Optional[Union[str, list[str]]] = empty_list()
    description: Optional[str] = None
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

        if self._is_empty(self.name):
            self.MissingRequiredField("name")
        if not isinstance(self.name, str):
            self.name = str(self.name)

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

        if self.description is not None and not isinstance(self.description, str):
            self.description = str(self.description)

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
class HasStructure(YAMLRoot):
    """
    Mixin структуры данных носителя. structure_ref — ссылка на DataStructure (range=DataStructure, ADR-038). Диалект
    схемы живёт на DataStructure.schema_dialect.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["HasStructure"]
    class_class_curie: ClassVar[str] = "dams:HasStructure"
    class_name: ClassVar[str] = "HasStructure"
    class_model_uri: ClassVar[URIRef] = DAMS.HasStructure

    structure_ref: Optional[Union[str, DataStructureElementId]] = None
    data_format: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.structure_ref is not None and not isinstance(self.structure_ref, DataStructureElementId):
            self.structure_ref = DataStructureElementId(self.structure_ref)

        if self.data_format is not None and not isinstance(self.data_format, str):
            self.data_format = str(self.data_format)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class HasProtocolBinding(YAMLRoot):
    """
    Mixin протокола доступа для точки доступа (AccessPoint).
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["HasProtocolBinding"]
    class_class_curie: ClassVar[str] = "dams:HasProtocolBinding"
    class_name: ClassVar[str] = "HasProtocolBinding"
    class_model_uri: ClassVar[URIRef] = DAMS.HasProtocolBinding

    protocol: Optional[str] = None
    protocol_version: Optional[str] = None
    binding_ref: Optional[Union[str, URIorCURIE]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.protocol is not None and not isinstance(self.protocol, str):
            self.protocol = str(self.protocol)

        if self.protocol_version is not None and not isinstance(self.protocol_version, str):
            self.protocol_version = str(self.protocol_version)

        if self.binding_ref is not None and not isinstance(self.binding_ref, URIorCURIE):
            self.binding_ref = URIorCURIE(self.binding_ref)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Contains(YAMLRoot):
    """
    Mixin контейнерности. child_refs не хранятся: выводятся из parent_ref.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["Contains"]
    class_class_curie: ClassVar[str] = "dams:Contains"
    class_name: ClassVar[str] = "Contains"
    class_model_uri: ClassVar[URIRef] = DAMS.Contains

    containment_kind: Optional[Union[str, "ContainmentKindEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.containment_kind is not None and not isinstance(self.containment_kind, ContainmentKindEnum):
            self.containment_kind = ContainmentKindEnum(self.containment_kind)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class HasLocation(YAMLRoot):
    """
    Mixin расположения носителя или точки доступа.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["HasLocation"]
    class_class_curie: ClassVar[str] = "dams:HasLocation"
    class_name: ClassVar[str] = "HasLocation"
    class_model_uri: ClassVar[URIRef] = DAMS.HasLocation

    location_uri: Optional[Union[str, URI]] = None
    region: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.location_uri is not None and not isinstance(self.location_uri, URI):
            self.location_uri = URI(self.location_uri)

        if self.region is not None and not isinstance(self.region, str):
            self.region = str(self.region)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class TechnicalAsset(ModelElement):
    """
    Квант данных: адресуемый технический объект управления. Имеет собственный идентификатор, систему-владельца,
    расположение или способ доступа, жизненный цикл, владельца, классификацию и роль в lineage. Поля, колонки и узлы
    схем квантами НЕ являются (ADR-C).
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["TechnicalAsset"]
    class_class_curie: ClassVar[str] = "dams:TechnicalAsset"
    class_name: ClassVar[str] = "TechnicalAsset"
    class_model_uri: ClassVar[URIRef] = DAMS.TechnicalAsset

    element_id: Union[str, TechnicalAssetElementId] = None
    name: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    asset_namespace: str = None
    qualified_name: str = None
    native_name: str = None
    system_ref: Union[str, ITSystemRegistryId] = None
    asset_kind: str = None
    description: str = None
    parent_ref: Optional[Union[str, TechnicalAssetElementId]] = None
    technology: Optional[str] = None
    lineage_role: Optional[Union[str, "LineageRoleEnum"]] = None
    direction: Optional[Union[str, "FlowDirectionEnum"]] = None
    solution_ref: Optional[Union[str, ITSolutionRegistryId]] = None
    data_owner_ref: Optional[Union[str, RoleRegistryId]] = None
    data_steward_ref: Optional[Union[str, RoleRegistryId]] = None
    owning_unit_ref: Optional[Union[str, OrganizationUnitRegistryId]] = None
    ownership_inheritance_rule: Optional[str] = None
    governance_classification: Optional[Union[str, "GovernanceClassificationEnum"]] = None
    security_classification: Optional[Union[str, "SecurityClassificationEnum"]] = None
    sensitivity_term_refs: Optional[Union[Union[str, DataClassificationTermRegistryId], list[Union[str, DataClassificationTermRegistryId]]]] = empty_list()
    classification_source: Optional[str] = None
    classification_rationale: Optional[str] = None
    policy_refs: Optional[Union[Union[str, PolicyRegistryId], list[Union[str, PolicyRegistryId]]]] = empty_list()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.asset_namespace):
            self.MissingRequiredField("asset_namespace")
        if not isinstance(self.asset_namespace, str):
            self.asset_namespace = str(self.asset_namespace)

        if self._is_empty(self.qualified_name):
            self.MissingRequiredField("qualified_name")
        if not isinstance(self.qualified_name, str):
            self.qualified_name = str(self.qualified_name)

        if self._is_empty(self.native_name):
            self.MissingRequiredField("native_name")
        if not isinstance(self.native_name, str):
            self.native_name = str(self.native_name)

        if self._is_empty(self.system_ref):
            self.MissingRequiredField("system_ref")
        if not isinstance(self.system_ref, ITSystemRegistryId):
            self.system_ref = ITSystemRegistryId(self.system_ref)

        if self._is_empty(self.asset_kind):
            self.MissingRequiredField("asset_kind")
        if not isinstance(self.asset_kind, str):
            self.asset_kind = str(self.asset_kind)

        if self._is_empty(self.description):
            self.MissingRequiredField("description")
        if not isinstance(self.description, str):
            self.description = str(self.description)

        if self.parent_ref is not None and not isinstance(self.parent_ref, TechnicalAssetElementId):
            self.parent_ref = TechnicalAssetElementId(self.parent_ref)

        if self.technology is not None and not isinstance(self.technology, str):
            self.technology = str(self.technology)

        if self.lineage_role is not None and not isinstance(self.lineage_role, LineageRoleEnum):
            self.lineage_role = LineageRoleEnum(self.lineage_role)

        if self.direction is not None and not isinstance(self.direction, FlowDirectionEnum):
            self.direction = FlowDirectionEnum(self.direction)

        if self.solution_ref is not None and not isinstance(self.solution_ref, ITSolutionRegistryId):
            self.solution_ref = ITSolutionRegistryId(self.solution_ref)

        if self.data_owner_ref is not None and not isinstance(self.data_owner_ref, RoleRegistryId):
            self.data_owner_ref = RoleRegistryId(self.data_owner_ref)

        if self.data_steward_ref is not None and not isinstance(self.data_steward_ref, RoleRegistryId):
            self.data_steward_ref = RoleRegistryId(self.data_steward_ref)

        if self.owning_unit_ref is not None and not isinstance(self.owning_unit_ref, OrganizationUnitRegistryId):
            self.owning_unit_ref = OrganizationUnitRegistryId(self.owning_unit_ref)

        if self.ownership_inheritance_rule is not None and not isinstance(self.ownership_inheritance_rule, str):
            self.ownership_inheritance_rule = str(self.ownership_inheritance_rule)

        if self.governance_classification is not None and not isinstance(self.governance_classification, GovernanceClassificationEnum):
            self.governance_classification = GovernanceClassificationEnum(self.governance_classification)

        if self.security_classification is not None and not isinstance(self.security_classification, SecurityClassificationEnum):
            self.security_classification = SecurityClassificationEnum(self.security_classification)

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
class DataCarrier(TechnicalAsset):
    """
    Носитель данных: хранит или передаёт данные (таблица, файл, топик, сообщение и т.п.).
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["DataCarrier"]
    class_class_curie: ClassVar[str] = "dams:DataCarrier"
    class_name: ClassVar[str] = "DataCarrier"
    class_model_uri: ClassVar[URIRef] = DAMS.DataCarrier

    element_id: Union[str, DataCarrierElementId] = None
    name: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    asset_namespace: str = None
    qualified_name: str = None
    native_name: str = None
    system_ref: Union[str, ITSystemRegistryId] = None
    description: str = None
    asset_kind: Union[str, "DataCarrierKindEnum"] = None
    mapping_coverage_status: Optional[Union[str, "MappingCoverageStatusEnum"]] = None
    mapping_rationale: Optional[str] = None
    structure_ref: Optional[Union[str, DataStructureElementId]] = None
    data_format: Optional[str] = None
    location_uri: Optional[Union[str, URI]] = None
    region: Optional[str] = None
    containment_kind: Optional[Union[str, "ContainmentKindEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, DataCarrierElementId):
            self.element_id = DataCarrierElementId(self.element_id)

        if self._is_empty(self.asset_kind):
            self.MissingRequiredField("asset_kind")
        if not isinstance(self.asset_kind, DataCarrierKindEnum):
            self.asset_kind = DataCarrierKindEnum(self.asset_kind)

        if self.mapping_coverage_status is not None and not isinstance(self.mapping_coverage_status, MappingCoverageStatusEnum):
            self.mapping_coverage_status = MappingCoverageStatusEnum(self.mapping_coverage_status)

        if self.mapping_rationale is not None and not isinstance(self.mapping_rationale, str):
            self.mapping_rationale = str(self.mapping_rationale)

        if self.structure_ref is not None and not isinstance(self.structure_ref, DataStructureElementId):
            self.structure_ref = DataStructureElementId(self.structure_ref)

        if self.data_format is not None and not isinstance(self.data_format, str):
            self.data_format = str(self.data_format)

        if self.location_uri is not None and not isinstance(self.location_uri, URI):
            self.location_uri = URI(self.location_uri)

        if self.region is not None and not isinstance(self.region, str):
            self.region = str(self.region)

        if self.containment_kind is not None and not isinstance(self.containment_kind, ContainmentKindEnum):
            self.containment_kind = ContainmentKindEnum(self.containment_kind)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class AccessPoint(TechnicalAsset):
    """
    Точка доступа к данным: интерфейс, операция или канал. Сама данные не несёт; указывает на носители через
    serves_refs.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["AccessPoint"]
    class_class_curie: ClassVar[str] = "dams:AccessPoint"
    class_name: ClassVar[str] = "AccessPoint"
    class_model_uri: ClassVar[URIRef] = DAMS.AccessPoint

    element_id: Union[str, AccessPointElementId] = None
    name: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    asset_namespace: str = None
    qualified_name: str = None
    native_name: str = None
    system_ref: Union[str, ITSystemRegistryId] = None
    description: str = None
    asset_kind: Union[str, "AccessPointKindEnum"] = None
    serves_refs: Optional[Union[Union[str, DataCarrierElementId], list[Union[str, DataCarrierElementId]]]] = empty_list()
    interface_ref: Optional[Union[str, AccessPointElementId]] = None
    operation_name: Optional[str] = None
    http_method: Optional[str] = None
    path_template: Optional[str] = None
    message_refs: Optional[Union[Union[str, MessageElementId], list[Union[str, MessageElementId]]]] = empty_list()
    direction: Optional[Union[str, "FlowDirectionEnum"]] = None
    protocol: Optional[str] = None
    protocol_version: Optional[str] = None
    binding_ref: Optional[Union[str, URIorCURIE]] = None
    location_uri: Optional[Union[str, URI]] = None
    region: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, AccessPointElementId):
            self.element_id = AccessPointElementId(self.element_id)

        if self._is_empty(self.asset_kind):
            self.MissingRequiredField("asset_kind")
        if not isinstance(self.asset_kind, AccessPointKindEnum):
            self.asset_kind = AccessPointKindEnum(self.asset_kind)

        if not isinstance(self.serves_refs, list):
            self.serves_refs = [self.serves_refs] if self.serves_refs is not None else []
        self.serves_refs = [v if isinstance(v, DataCarrierElementId) else DataCarrierElementId(v) for v in self.serves_refs]

        if self.interface_ref is not None and not isinstance(self.interface_ref, AccessPointElementId):
            self.interface_ref = AccessPointElementId(self.interface_ref)

        if self.operation_name is not None and not isinstance(self.operation_name, str):
            self.operation_name = str(self.operation_name)

        if self.http_method is not None and not isinstance(self.http_method, str):
            self.http_method = str(self.http_method)

        if self.path_template is not None and not isinstance(self.path_template, str):
            self.path_template = str(self.path_template)

        if not isinstance(self.message_refs, list):
            self.message_refs = [self.message_refs] if self.message_refs is not None else []
        self.message_refs = [v if isinstance(v, MessageElementId) else MessageElementId(v) for v in self.message_refs]

        if self.direction is not None and not isinstance(self.direction, FlowDirectionEnum):
            self.direction = FlowDirectionEnum(self.direction)

        if self.protocol is not None and not isinstance(self.protocol, str):
            self.protocol = str(self.protocol)

        if self.protocol_version is not None and not isinstance(self.protocol_version, str):
            self.protocol_version = str(self.protocol_version)

        if self.binding_ref is not None and not isinstance(self.binding_ref, URIorCURIE):
            self.binding_ref = URIorCURIE(self.binding_ref)

        if self.location_uri is not None and not isinstance(self.location_uri, URI):
            self.location_uri = URI(self.location_uri)

        if self.region is not None and not isinstance(self.region, str):
            self.region = str(self.region)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class DataContainer(TechnicalAsset):
    """
    Контейнер других активов (database, schema, bucket, broker, directory, cluster). Данных не несёт: structure_ref и
    data_format отсутствуют.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["DataContainer"]
    class_class_curie: ClassVar[str] = "dams:DataContainer"
    class_name: ClassVar[str] = "DataContainer"
    class_model_uri: ClassVar[URIRef] = DAMS.DataContainer

    element_id: Union[str, DataContainerElementId] = None
    name: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    asset_namespace: str = None
    qualified_name: str = None
    native_name: str = None
    system_ref: Union[str, ITSystemRegistryId] = None
    description: str = None
    asset_kind: Union[str, "DataContainerKindEnum"] = None
    direction: Optional[Union[str, "FlowDirectionEnum"]] = None
    containment_kind: Optional[Union[str, "ContainmentKindEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, DataContainerElementId):
            self.element_id = DataContainerElementId(self.element_id)

        if self._is_empty(self.asset_kind):
            self.MissingRequiredField("asset_kind")
        if not isinstance(self.asset_kind, DataContainerKindEnum):
            self.asset_kind = DataContainerKindEnum(self.asset_kind)

        if self.direction is not None and not isinstance(self.direction, FlowDirectionEnum):
            self.direction = FlowDirectionEnum(self.direction)

        if self.containment_kind is not None and not isinstance(self.containment_kind, ContainmentKindEnum):
            self.containment_kind = ContainmentKindEnum(self.containment_kind)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ExecutionAsset(TechnicalAsset):
    """
    Исполняемый актив (pipeline / job) с минимальной lineage-ролью.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["ExecutionAsset"]
    class_class_curie: ClassVar[str] = "dams:ExecutionAsset"
    class_name: ClassVar[str] = "ExecutionAsset"
    class_model_uri: ClassVar[URIRef] = DAMS.ExecutionAsset

    element_id: Union[str, ExecutionAssetElementId] = None
    name: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    asset_namespace: str = None
    qualified_name: str = None
    native_name: str = None
    system_ref: Union[str, ITSystemRegistryId] = None
    description: str = None
    asset_kind: Union[str, "ExecutionAssetKindEnum"] = None
    produces_refs: Optional[Union[Union[str, TechnicalAssetElementId], list[Union[str, TechnicalAssetElementId]]]] = empty_list()
    consumes_refs: Optional[Union[Union[str, TechnicalAssetElementId], list[Union[str, TechnicalAssetElementId]]]] = empty_list()
    direction: Optional[Union[str, "FlowDirectionEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, ExecutionAssetElementId):
            self.element_id = ExecutionAssetElementId(self.element_id)

        if self._is_empty(self.asset_kind):
            self.MissingRequiredField("asset_kind")
        if not isinstance(self.asset_kind, ExecutionAssetKindEnum):
            self.asset_kind = ExecutionAssetKindEnum(self.asset_kind)

        if not isinstance(self.produces_refs, list):
            self.produces_refs = [self.produces_refs] if self.produces_refs is not None else []
        self.produces_refs = [v if isinstance(v, TechnicalAssetElementId) else TechnicalAssetElementId(v) for v in self.produces_refs]

        if not isinstance(self.consumes_refs, list):
            self.consumes_refs = [self.consumes_refs] if self.consumes_refs is not None else []
        self.consumes_refs = [v if isinstance(v, TechnicalAssetElementId) else TechnicalAssetElementId(v) for v in self.consumes_refs]

        if self.direction is not None and not isinstance(self.direction, FlowDirectionEnum):
            self.direction = FlowDirectionEnum(self.direction)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ConceptualDomain(ModelElement):
    """
    Концептуальный домен значений: набор смыслов (ValueMeaning) или ссылка на внешнюю схему понятий. Допустим только в
    пакетах implementation_scope=enterprise.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["ConceptualDomain"]
    class_class_curie: ClassVar[str] = "dams:ConceptualDomain"
    class_name: ClassVar[str] = "ConceptualDomain"
    class_model_uri: ClassVar[URIRef] = DAMS.ConceptualDomain

    element_id: Union[str, ConceptualDomainElementId] = None
    name: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    conceptual_domain_kind: Union[str, "ConceptualDomainKindEnum"] = None
    description: str = None
    value_meanings: Optional[Union[dict[Union[str, ValueMeaningMeaningKey], Union[dict, "ValueMeaning"]], list[Union[dict, "ValueMeaning"]]]] = empty_dict()
    concept_scheme_uri: Optional[Union[str, URIorCURIE]] = None
    broader_domain_ref: Optional[Union[str, ConceptualDomainElementId]] = None
    data_owner_ref: Optional[Union[str, RoleRegistryId]] = None
    data_steward_ref: Optional[Union[str, RoleRegistryId]] = None
    owning_unit_ref: Optional[Union[str, OrganizationUnitRegistryId]] = None
    ownership_inheritance_rule: Optional[str] = None
    source_artifact_ref: Optional[Union[str, URI]] = None
    evidence_refs: Optional[Union[Union[str, URI], list[Union[str, URI]]]] = empty_list()
    approval_status: Optional[Union[str, "ApprovalStatusEnum"]] = None
    approved_by_ref: Optional[Union[str, RoleRegistryId]] = None
    approved_at: Optional[Union[str, XSDDateTime]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, ConceptualDomainElementId):
            self.element_id = ConceptualDomainElementId(self.element_id)

        if self._is_empty(self.conceptual_domain_kind):
            self.MissingRequiredField("conceptual_domain_kind")
        if not isinstance(self.conceptual_domain_kind, ConceptualDomainKindEnum):
            self.conceptual_domain_kind = ConceptualDomainKindEnum(self.conceptual_domain_kind)

        if self._is_empty(self.description):
            self.MissingRequiredField("description")
        if not isinstance(self.description, str):
            self.description = str(self.description)

        self._normalize_inlined_as_list(slot_name="value_meanings", slot_type=ValueMeaning, key_name="meaning_key", keyed=True)

        if self.concept_scheme_uri is not None and not isinstance(self.concept_scheme_uri, URIorCURIE):
            self.concept_scheme_uri = URIorCURIE(self.concept_scheme_uri)

        if self.broader_domain_ref is not None and not isinstance(self.broader_domain_ref, ConceptualDomainElementId):
            self.broader_domain_ref = ConceptualDomainElementId(self.broader_domain_ref)

        if self.data_owner_ref is not None and not isinstance(self.data_owner_ref, RoleRegistryId):
            self.data_owner_ref = RoleRegistryId(self.data_owner_ref)

        if self.data_steward_ref is not None and not isinstance(self.data_steward_ref, RoleRegistryId):
            self.data_steward_ref = RoleRegistryId(self.data_steward_ref)

        if self.owning_unit_ref is not None and not isinstance(self.owning_unit_ref, OrganizationUnitRegistryId):
            self.owning_unit_ref = OrganizationUnitRegistryId(self.owning_unit_ref)

        if self.ownership_inheritance_rule is not None and not isinstance(self.ownership_inheritance_rule, str):
            self.ownership_inheritance_rule = str(self.ownership_inheritance_rule)

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
class ValueMeaning(YAMLRoot):
    """
    Смысл допустимого значения внутри ConceptualDomain (встраиваемый, без lifecycle).
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["ValueMeaning"]
    class_class_curie: ClassVar[str] = "dams:ValueMeaning"
    class_name: ClassVar[str] = "ValueMeaning"
    class_model_uri: ClassVar[URIRef] = DAMS.ValueMeaning

    meaning_key: Union[str, ValueMeaningMeaningKey] = None
    meaning_label: Optional[str] = None
    meaning_definition: Optional[str] = None
    aliases: Optional[Union[str, list[str]]] = empty_list()
    meaning_term_ref: Optional[Union[str, URIorCURIE]] = None
    broader_meaning_key: Optional[str] = None
    meaning_status: Optional[Union[str, "LifecycleStatusEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.meaning_key):
            self.MissingRequiredField("meaning_key")
        if not isinstance(self.meaning_key, ValueMeaningMeaningKey):
            self.meaning_key = ValueMeaningMeaningKey(self.meaning_key)

        if self.meaning_label is not None and not isinstance(self.meaning_label, str):
            self.meaning_label = str(self.meaning_label)

        if self.meaning_definition is not None and not isinstance(self.meaning_definition, str):
            self.meaning_definition = str(self.meaning_definition)

        if not isinstance(self.aliases, list):
            self.aliases = [self.aliases] if self.aliases is not None else []
        self.aliases = [v if isinstance(v, str) else str(v) for v in self.aliases]

        if self.meaning_term_ref is not None and not isinstance(self.meaning_term_ref, URIorCURIE):
            self.meaning_term_ref = URIorCURIE(self.meaning_term_ref)

        if self.broader_meaning_key is not None and not isinstance(self.broader_meaning_key, str):
            self.broader_meaning_key = str(self.broader_meaning_key)

        if self.meaning_status is not None and not isinstance(self.meaning_status, LifecycleStatusEnum):
            self.meaning_status = LifecycleStatusEnum(self.meaning_status)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class DataType(ModelElement):
    """
    Корпоративный тип данных: семейство, параметры представления и соответствие XSD/LinkML. Допустим только в
    корпоративном реестре типов.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["DataType"]
    class_class_curie: ClassVar[str] = "dams:DataType"
    class_name: ClassVar[str] = "DataType"
    class_model_uri: ClassVar[URIRef] = DAMS.DataType

    element_id: Union[str, DataTypeElementId] = None
    name: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    type_name: str = None
    type_family: Union[str, "TypeFamilyEnum"] = None
    description: str = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    max_length: Optional[int] = None
    min_length: Optional[int] = None
    datatype_timezone_policy: Optional[Union[str, "TimezonePolicyEnum"]] = None
    charset: Optional[str] = None
    xsd_datatype: Optional[Union[str, URIorCURIE]] = None
    linkml_type: Optional[str] = None
    base_type_ref: Optional[Union[str, DataTypeElementId]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, DataTypeElementId):
            self.element_id = DataTypeElementId(self.element_id)

        if self._is_empty(self.type_name):
            self.MissingRequiredField("type_name")
        if not isinstance(self.type_name, str):
            self.type_name = str(self.type_name)

        if self._is_empty(self.type_family):
            self.MissingRequiredField("type_family")
        if not isinstance(self.type_family, TypeFamilyEnum):
            self.type_family = TypeFamilyEnum(self.type_family)

        if self._is_empty(self.description):
            self.MissingRequiredField("description")
        if not isinstance(self.description, str):
            self.description = str(self.description)

        if self.precision is not None and not isinstance(self.precision, int):
            self.precision = int(self.precision)

        if self.scale is not None and not isinstance(self.scale, int):
            self.scale = int(self.scale)

        if self.max_length is not None and not isinstance(self.max_length, int):
            self.max_length = int(self.max_length)

        if self.min_length is not None and not isinstance(self.min_length, int):
            self.min_length = int(self.min_length)

        if self.datatype_timezone_policy is not None and not isinstance(self.datatype_timezone_policy, TimezonePolicyEnum):
            self.datatype_timezone_policy = TimezonePolicyEnum(self.datatype_timezone_policy)

        if self.charset is not None and not isinstance(self.charset, str):
            self.charset = str(self.charset)

        if self.xsd_datatype is not None and not isinstance(self.xsd_datatype, URIorCURIE):
            self.xsd_datatype = URIorCURIE(self.xsd_datatype)

        if self.linkml_type is not None and not isinstance(self.linkml_type, str):
            self.linkml_type = str(self.linkml_type)

        if self.base_type_ref is not None and not isinstance(self.base_type_ref, DataTypeElementId):
            self.base_type_ref = DataTypeElementId(self.base_type_ref)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class NativeTypeBinding(YAMLRoot):
    """
    Привязка нативного типа диалекта (SQL, JSON Schema и т.п.) к корпоративному DataType с оценкой потери точности.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["NativeTypeBinding"]
    class_class_curie: ClassVar[str] = "dams:NativeTypeBinding"
    class_name: ClassVar[str] = "NativeTypeBinding"
    class_model_uri: ClassVar[URIRef] = DAMS.NativeTypeBinding

    binding_id: Union[str, NativeTypeBindingBindingId] = None
    dialect: str = None
    dialect_native_type: str = None
    data_type_ref: Union[str, DataTypeElementId] = None
    lossiness: Union[str, "LossinessEnum"] = None
    parameter_mapping: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.binding_id):
            self.MissingRequiredField("binding_id")
        if not isinstance(self.binding_id, NativeTypeBindingBindingId):
            self.binding_id = NativeTypeBindingBindingId(self.binding_id)

        if self._is_empty(self.dialect):
            self.MissingRequiredField("dialect")
        if not isinstance(self.dialect, str):
            self.dialect = str(self.dialect)

        if self._is_empty(self.dialect_native_type):
            self.MissingRequiredField("dialect_native_type")
        if not isinstance(self.dialect_native_type, str):
            self.dialect_native_type = str(self.dialect_native_type)

        if self._is_empty(self.data_type_ref):
            self.MissingRequiredField("data_type_ref")
        if not isinstance(self.data_type_ref, DataTypeElementId):
            self.data_type_ref = DataTypeElementId(self.data_type_ref)

        if self._is_empty(self.lossiness):
            self.MissingRequiredField("lossiness")
        if not isinstance(self.lossiness, LossinessEnum):
            self.lossiness = LossinessEnum(self.lossiness)

        if self.parameter_mapping is not None and not isinstance(self.parameter_mapping, str):
            self.parameter_mapping = str(self.parameter_mapping)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ValueDomain(ModelElement):
    """
    Представление значений: тип, формат, единица, допустимые значения или ссылка на внешний набор. Допустим в пакетах
    enterprise и solution.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["ValueDomain"]
    class_class_curie: ClassVar[str] = "dams:ValueDomain"
    class_name: ClassVar[str] = "ValueDomain"
    class_model_uri: ClassVar[URIRef] = DAMS.ValueDomain

    element_id: Union[str, ValueDomainElementId] = None
    name: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    value_domain_kind: Union[str, "ValueDomainKindEnum"] = None
    data_type_ref: Union[str, DataTypeElementId] = None
    description: str = None
    conceptual_domain_ref: Optional[Union[str, ConceptualDomainElementId]] = None
    unit_code: Optional[str] = None
    format_pattern: Optional[str] = None
    min_value: Optional[str] = None
    max_value: Optional[str] = None
    permissible_values: Optional[Union[dict[Union[str, PermissibleValueValueCode], Union[dict, "PermissibleValue"]], list[Union[dict, "PermissibleValue"]]]] = empty_dict()
    value_set_source: Optional[Union[str, URIorCURIE]] = None
    dynamic_query: Optional[Union[dict, "ValueSetQuery"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, ValueDomainElementId):
            self.element_id = ValueDomainElementId(self.element_id)

        if self._is_empty(self.value_domain_kind):
            self.MissingRequiredField("value_domain_kind")
        if not isinstance(self.value_domain_kind, ValueDomainKindEnum):
            self.value_domain_kind = ValueDomainKindEnum(self.value_domain_kind)

        if self._is_empty(self.data_type_ref):
            self.MissingRequiredField("data_type_ref")
        if not isinstance(self.data_type_ref, DataTypeElementId):
            self.data_type_ref = DataTypeElementId(self.data_type_ref)

        if self._is_empty(self.description):
            self.MissingRequiredField("description")
        if not isinstance(self.description, str):
            self.description = str(self.description)

        if self.conceptual_domain_ref is not None and not isinstance(self.conceptual_domain_ref, ConceptualDomainElementId):
            self.conceptual_domain_ref = ConceptualDomainElementId(self.conceptual_domain_ref)

        if self.unit_code is not None and not isinstance(self.unit_code, str):
            self.unit_code = str(self.unit_code)

        if self.format_pattern is not None and not isinstance(self.format_pattern, str):
            self.format_pattern = str(self.format_pattern)

        if self.min_value is not None and not isinstance(self.min_value, str):
            self.min_value = str(self.min_value)

        if self.max_value is not None and not isinstance(self.max_value, str):
            self.max_value = str(self.max_value)

        self._normalize_inlined_as_list(slot_name="permissible_values", slot_type=PermissibleValue, key_name="value_code", keyed=True)

        if self.value_set_source is not None and not isinstance(self.value_set_source, URIorCURIE):
            self.value_set_source = URIorCURIE(self.value_set_source)

        if self.dynamic_query is not None and not isinstance(self.dynamic_query, ValueSetQuery):
            self.dynamic_query = ValueSetQuery(**as_dict(self.dynamic_query))

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class PermissibleValue(YAMLRoot):
    """
    Допустимое значение внутри ValueDomain (встраиваемый).
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["PermissibleValue"]
    class_class_curie: ClassVar[str] = "dams:PermissibleValue"
    class_name: ClassVar[str] = "PermissibleValue"
    class_model_uri: ClassVar[URIRef] = DAMS.PermissibleValue

    value_code: Union[str, PermissibleValueValueCode] = None
    value_label: Optional[str] = None
    value_definition: Optional[str] = None
    value_meaning_key: Optional[str] = None
    meaning_term_ref: Optional[Union[str, URIorCURIE]] = None
    ordinal: Optional[int] = None
    value_status: Optional[Union[str, "LifecycleStatusEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.value_code):
            self.MissingRequiredField("value_code")
        if not isinstance(self.value_code, PermissibleValueValueCode):
            self.value_code = PermissibleValueValueCode(self.value_code)

        if self.value_label is not None and not isinstance(self.value_label, str):
            self.value_label = str(self.value_label)

        if self.value_definition is not None and not isinstance(self.value_definition, str):
            self.value_definition = str(self.value_definition)

        if self.value_meaning_key is not None and not isinstance(self.value_meaning_key, str):
            self.value_meaning_key = str(self.value_meaning_key)

        if self.meaning_term_ref is not None and not isinstance(self.meaning_term_ref, URIorCURIE):
            self.meaning_term_ref = URIorCURIE(self.meaning_term_ref)

        if self.ordinal is not None and not isinstance(self.ordinal, int):
            self.ordinal = int(self.ordinal)

        if self.value_status is not None and not isinstance(self.value_status, LifecycleStatusEnum):
            self.value_status = LifecycleStatusEnum(self.value_status)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ValueSetQuery(YAMLRoot):
    """
    Динамический запрос набора значений по образцу LinkML reachable_from (source ontology, узлы, типы связей).
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["ValueSetQuery"]
    class_class_curie: ClassVar[str] = "dams:ValueSetQuery"
    class_name: ClassVar[str] = "ValueSetQuery"
    class_model_uri: ClassVar[URIRef] = DAMS.ValueSetQuery

    value_set_query_id: Union[str, ValueSetQueryValueSetQueryId] = None
    source_ontology: Union[str, URIorCURIE] = None
    source_nodes: Optional[Union[Union[str, URIorCURIE], list[Union[str, URIorCURIE]]]] = empty_list()
    relationship_types: Optional[Union[Union[str, URIorCURIE], list[Union[str, URIorCURIE]]]] = empty_list()
    include_self: Optional[Union[bool, Bool]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.value_set_query_id):
            self.MissingRequiredField("value_set_query_id")
        if not isinstance(self.value_set_query_id, ValueSetQueryValueSetQueryId):
            self.value_set_query_id = ValueSetQueryValueSetQueryId(self.value_set_query_id)

        if self._is_empty(self.source_ontology):
            self.MissingRequiredField("source_ontology")
        if not isinstance(self.source_ontology, URIorCURIE):
            self.source_ontology = URIorCURIE(self.source_ontology)

        if not isinstance(self.source_nodes, list):
            self.source_nodes = [self.source_nodes] if self.source_nodes is not None else []
        self.source_nodes = [v if isinstance(v, URIorCURIE) else URIorCURIE(v) for v in self.source_nodes]

        if not isinstance(self.relationship_types, list):
            self.relationship_types = [self.relationship_types] if self.relationship_types is not None else []
        self.relationship_types = [v if isinstance(v, URIorCURIE) else URIorCURIE(v) for v in self.relationship_types]

        if self.include_self is not None and not isinstance(self.include_self, Bool):
            self.include_self = Bool(self.include_self)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class EmbeddedElement(YAMLRoot):
    """
    Встраиваемый вспомогательный объект без собственного жизненного цикла и глобального element_id. Идентичность
    локальна относительно родителя (local_key). Не путать с IdentifiedElement (ADR-038 / ADR-044).
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["EmbeddedElement"]
    class_class_curie: ClassVar[str] = "dams:EmbeddedElement"
    class_name: ClassVar[str] = "EmbeddedElement"
    class_model_uri: ClassVar[URIRef] = DAMS.EmbeddedElement

    local_key: Union[str, EmbeddedElementLocalKey] = None
    description: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.local_key):
            self.MissingRequiredField("local_key")
        if not isinstance(self.local_key, EmbeddedElementLocalKey):
            self.local_key = EmbeddedElementLocalKey(self.local_key)

        if self.description is not None and not isinstance(self.description, str):
            self.description = str(self.description)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class DataStructure(ModelElement):
    """
    Именованная версия структуры данных: корень дерева SchemaNode с форматом и опциональным диалектом (ADR-038).
    Хранит плоский список узлов (nodes + root_local_key).
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["DataStructure"]
    class_class_curie: ClassVar[str] = "dams:DataStructure"
    class_name: ClassVar[str] = "DataStructure"
    class_model_uri: ClassVar[URIRef] = DAMS.DataStructure

    element_id: Union[str, DataStructureElementId] = None
    name: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    schema_format: Union[str, "SchemaFormatEnum"] = None
    structure_version: Union[str, SemVer] = None
    root_local_key: str = None
    nodes: Union[dict[Union[str, SchemaNodeLocalKey], Union[dict, "SchemaNode"]], list[Union[dict, "SchemaNode"]]] = empty_dict()
    schema_dialect: Optional[Union[str, URI]] = None
    source_artifact_ref: Optional[Union[str, URI]] = None
    source_pointer: Optional[str] = None
    content_digest: Optional[Union[str, Sha256Digest]] = None
    previous_version_ref: Optional[Union[str, DataStructureElementId]] = None
    description: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, DataStructureElementId):
            self.element_id = DataStructureElementId(self.element_id)

        if self._is_empty(self.schema_format):
            self.MissingRequiredField("schema_format")
        if not isinstance(self.schema_format, SchemaFormatEnum):
            self.schema_format = SchemaFormatEnum(self.schema_format)

        if self._is_empty(self.structure_version):
            self.MissingRequiredField("structure_version")
        if not isinstance(self.structure_version, SemVer):
            self.structure_version = SemVer(self.structure_version)

        if self._is_empty(self.root_local_key):
            self.MissingRequiredField("root_local_key")
        if not isinstance(self.root_local_key, str):
            self.root_local_key = str(self.root_local_key)

        if self._is_empty(self.nodes):
            self.MissingRequiredField("nodes")
        self._normalize_inlined_as_list(slot_name="nodes", slot_type=SchemaNode, key_name="local_key", keyed=True)

        if self.schema_dialect is not None and not isinstance(self.schema_dialect, URI):
            self.schema_dialect = URI(self.schema_dialect)

        if self.source_artifact_ref is not None and not isinstance(self.source_artifact_ref, URI):
            self.source_artifact_ref = URI(self.source_artifact_ref)

        if self.source_pointer is not None and not isinstance(self.source_pointer, str):
            self.source_pointer = str(self.source_pointer)

        if self.content_digest is not None and not isinstance(self.content_digest, Sha256Digest):
            self.content_digest = Sha256Digest(self.content_digest)

        if self.previous_version_ref is not None and not isinstance(self.previous_version_ref, DataStructureElementId):
            self.previous_version_ref = DataStructureElementId(self.previous_version_ref)

        if self.description is not None and not isinstance(self.description, str):
            self.description = str(self.description)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class SchemaNode(EmbeddedElement):
    """
    Узел дерева структуры. Идентичность (DataStructure.element_id, local_key). Рёбра children/item_node — строки
    local_key (плоская форма, ADR-038). Форма и физика в одном узле (как ODCS).
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["SchemaNode"]
    class_class_curie: ClassVar[str] = "dams:SchemaNode"
    class_name: ClassVar[str] = "SchemaNode"
    class_model_uri: ClassVar[URIRef] = DAMS.SchemaNode

    local_key: Union[str, SchemaNodeLocalKey] = None
    native_name: str = None
    node_kind: Union[str, "SchemaNodeKindEnum"] = None
    native_type: str = None
    required: Union[bool, Bool] = None
    children: Optional[Union[str, list[str]]] = empty_list()
    item_node: Optional[str] = None
    data_type_ref: Optional[Union[str, DataTypeElementId]] = None
    nullable: Optional[Union[bool, Bool]] = None
    min_occurs: Optional[int] = None
    max_occurs: Optional[int] = None
    ordinal_position: Optional[int] = None
    reference_target: Optional[Union[str, URIorCURIE]] = None
    realizes_attribute_ref: Optional[Union[str, LogicalAttributeElementId]] = None
    constraint_expressions: Optional[Union[str, list[str]]] = empty_list()
    default_value: Optional[str] = None
    mapping_coverage_status: Optional[Union[str, "MappingCoverageStatusEnum"]] = None
    mapping_rationale: Optional[str] = None
    column_position: Optional[int] = None
    is_primary_key: Optional[Union[bool, Bool]] = None
    is_unique: Optional[Union[bool, Bool]] = None
    foreign_key_target: Optional[Union[str, URIorCURIE]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.local_key):
            self.MissingRequiredField("local_key")
        if not isinstance(self.local_key, SchemaNodeLocalKey):
            self.local_key = SchemaNodeLocalKey(self.local_key)

        if self._is_empty(self.native_name):
            self.MissingRequiredField("native_name")
        if not isinstance(self.native_name, str):
            self.native_name = str(self.native_name)

        if self._is_empty(self.node_kind):
            self.MissingRequiredField("node_kind")
        if not isinstance(self.node_kind, SchemaNodeKindEnum):
            self.node_kind = SchemaNodeKindEnum(self.node_kind)

        if self._is_empty(self.native_type):
            self.MissingRequiredField("native_type")
        if not isinstance(self.native_type, str):
            self.native_type = str(self.native_type)

        if self._is_empty(self.required):
            self.MissingRequiredField("required")
        if not isinstance(self.required, Bool):
            self.required = Bool(self.required)

        if not isinstance(self.children, list):
            self.children = [self.children] if self.children is not None else []
        self.children = [v if isinstance(v, str) else str(v) for v in self.children]

        if self.item_node is not None and not isinstance(self.item_node, str):
            self.item_node = str(self.item_node)

        if self.data_type_ref is not None and not isinstance(self.data_type_ref, DataTypeElementId):
            self.data_type_ref = DataTypeElementId(self.data_type_ref)

        if self.nullable is not None and not isinstance(self.nullable, Bool):
            self.nullable = Bool(self.nullable)

        if self.min_occurs is not None and not isinstance(self.min_occurs, int):
            self.min_occurs = int(self.min_occurs)

        if self.max_occurs is not None and not isinstance(self.max_occurs, int):
            self.max_occurs = int(self.max_occurs)

        if self.ordinal_position is not None and not isinstance(self.ordinal_position, int):
            self.ordinal_position = int(self.ordinal_position)

        if self.reference_target is not None and not isinstance(self.reference_target, URIorCURIE):
            self.reference_target = URIorCURIE(self.reference_target)

        if self.realizes_attribute_ref is not None and not isinstance(self.realizes_attribute_ref, LogicalAttributeElementId):
            self.realizes_attribute_ref = LogicalAttributeElementId(self.realizes_attribute_ref)

        if not isinstance(self.constraint_expressions, list):
            self.constraint_expressions = [self.constraint_expressions] if self.constraint_expressions is not None else []
        self.constraint_expressions = [v if isinstance(v, str) else str(v) for v in self.constraint_expressions]

        if self.default_value is not None and not isinstance(self.default_value, str):
            self.default_value = str(self.default_value)

        if self.mapping_coverage_status is not None and not isinstance(self.mapping_coverage_status, MappingCoverageStatusEnum):
            self.mapping_coverage_status = MappingCoverageStatusEnum(self.mapping_coverage_status)

        if self.mapping_rationale is not None and not isinstance(self.mapping_rationale, str):
            self.mapping_rationale = str(self.mapping_rationale)

        if self.column_position is not None and not isinstance(self.column_position, int):
            self.column_position = int(self.column_position)

        if self.is_primary_key is not None and not isinstance(self.is_primary_key, Bool):
            self.is_primary_key = Bool(self.is_primary_key)

        if self.is_unique is not None and not isinstance(self.is_unique, Bool):
            self.is_unique = Bool(self.is_unique)

        if self.foreign_key_target is not None and not isinstance(self.foreign_key_target, URIorCURIE):
            self.foreign_key_target = URIorCURIE(self.foreign_key_target)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Message(ModelElement):
    """
    Элемент интеграционной модели: сообщение с payload/headers структурами. Не TechnicalAsset (нет asset_namespace /
    qualified_name; не carrier_refs). AccessPoint (operation|channel) ссылается через message_refs (ADR-040). Класс в
    moex-structure, чтобы ModelPackage и AccessPoint ссылались без цикла core↔integration (ADR-040).
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["Message"]
    class_class_curie: ClassVar[str] = "dams:Message"
    class_name: ClassVar[str] = "Message"
    class_model_uri: ClassVar[URIRef] = DAMS.Message

    element_id: Union[str, MessageElementId] = None
    name: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    payload_structure_ref: Union[str, DataStructureElementId] = None
    headers_structure_ref: Optional[Union[str, DataStructureElementId]] = None
    content_type: Optional[str] = None
    envelope_kind: Optional[Union[str, "EnvelopeKindEnum"]] = None
    envelope_ref: Optional[Union[str, URIorCURIE]] = None
    correlation_hint: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, MessageElementId):
            self.element_id = MessageElementId(self.element_id)

        if self._is_empty(self.payload_structure_ref):
            self.MissingRequiredField("payload_structure_ref")
        if not isinstance(self.payload_structure_ref, DataStructureElementId):
            self.payload_structure_ref = DataStructureElementId(self.payload_structure_ref)

        if self.headers_structure_ref is not None and not isinstance(self.headers_structure_ref, DataStructureElementId):
            self.headers_structure_ref = DataStructureElementId(self.headers_structure_ref)

        if self.content_type is not None and not isinstance(self.content_type, str):
            self.content_type = str(self.content_type)

        if self.envelope_kind is not None and not isinstance(self.envelope_kind, EnvelopeKindEnum):
            self.envelope_kind = EnvelopeKindEnum(self.envelope_kind)

        if self.envelope_ref is not None and not isinstance(self.envelope_ref, URIorCURIE):
            self.envelope_ref = URIorCURIE(self.envelope_ref)

        if self.correlation_hint is not None and not isinstance(self.correlation_hint, str):
            self.correlation_hint = str(self.correlation_hint)

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
    description: str = None
    contract_ref: Optional[Union[str, DataContractReferenceRegistryId]] = None
    entity_bindings: Optional[Union[dict[Union[str, DataFlowEntityBindingElementId], Union[dict, "DataFlowEntityBinding"]], list[Union[dict, "DataFlowEntityBinding"]]]] = empty_dict()
    data_owner_ref: Optional[Union[str, RoleRegistryId]] = None
    data_steward_ref: Optional[Union[str, RoleRegistryId]] = None
    owning_unit_ref: Optional[Union[str, OrganizationUnitRegistryId]] = None
    ownership_inheritance_rule: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, DataFlowElementId):
            self.element_id = DataFlowElementId(self.element_id)

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

        if self._is_empty(self.description):
            self.MissingRequiredField("description")
        if not isinstance(self.description, str):
            self.description = str(self.description)

        if self.contract_ref is not None and not isinstance(self.contract_ref, DataContractReferenceRegistryId):
            self.contract_ref = DataContractReferenceRegistryId(self.contract_ref)

        self._normalize_inlined_as_list(slot_name="entity_bindings", slot_type=DataFlowEntityBinding, key_name="element_id", keyed=True)

        if self.data_owner_ref is not None and not isinstance(self.data_owner_ref, RoleRegistryId):
            self.data_owner_ref = RoleRegistryId(self.data_owner_ref)

        if self.data_steward_ref is not None and not isinstance(self.data_steward_ref, RoleRegistryId):
            self.data_steward_ref = RoleRegistryId(self.data_steward_ref)

        if self.owning_unit_ref is not None and not isinstance(self.owning_unit_ref, OrganizationUnitRegistryId):
            self.owning_unit_ref = OrganizationUnitRegistryId(self.owning_unit_ref)

        if self.ownership_inheritance_rule is not None and not isinstance(self.ownership_inheritance_rule, str):
            self.ownership_inheritance_rule = str(self.ownership_inheritance_rule)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class DataFlowEntityBinding(ModelElement):
    """
    Связь потока с логическими сущностями, атрибутами и носителями данных модели решения.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["DataFlowEntityBinding"]
    class_class_curie: ClassVar[str] = "dams:DataFlowEntityBinding"
    class_name: ClassVar[str] = "DataFlowEntityBinding"
    class_model_uri: ClassVar[URIRef] = DAMS.DataFlowEntityBinding

    element_id: Union[str, DataFlowEntityBindingElementId] = None
    name: str = None
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    flow_ref: Union[str, DataFlowElementId] = None
    source_model_ref: Union[str, URI] = None
    logical_entity_ref: Union[str, LogicalEntityElementId] = None
    description: str = None
    logical_attribute_refs: Optional[Union[Union[str, LogicalAttributeElementId], list[Union[str, LogicalAttributeElementId]]]] = empty_list()
    carrier_refs: Optional[Union[Union[str, DataCarrierElementId], list[Union[str, DataCarrierElementId]]]] = empty_list()
    schema_node_refs: Optional[Union[Union[str, URIorCURIE], list[Union[str, URIorCURIE]]]] = empty_list()
    transformation_mapping_refs: Optional[Union[Union[str, MappingElementId], list[Union[str, MappingElementId]]]] = empty_list()
    direction: Optional[Union[str, "FlowDirectionEnum"]] = None

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

        if self._is_empty(self.description):
            self.MissingRequiredField("description")
        if not isinstance(self.description, str):
            self.description = str(self.description)

        if not isinstance(self.logical_attribute_refs, list):
            self.logical_attribute_refs = [self.logical_attribute_refs] if self.logical_attribute_refs is not None else []
        self.logical_attribute_refs = [v if isinstance(v, LogicalAttributeElementId) else LogicalAttributeElementId(v) for v in self.logical_attribute_refs]

        if not isinstance(self.carrier_refs, list):
            self.carrier_refs = [self.carrier_refs] if self.carrier_refs is not None else []
        self.carrier_refs = [v if isinstance(v, DataCarrierElementId) else DataCarrierElementId(v) for v in self.carrier_refs]

        if not isinstance(self.schema_node_refs, list):
            self.schema_node_refs = [self.schema_node_refs] if self.schema_node_refs is not None else []
        self.schema_node_refs = [v if isinstance(v, URIorCURIE) else URIorCURIE(v) for v in self.schema_node_refs]

        if not isinstance(self.transformation_mapping_refs, list):
            self.transformation_mapping_refs = [self.transformation_mapping_refs] if self.transformation_mapping_refs is not None else []
        self.transformation_mapping_refs = [v if isinstance(v, MappingElementId) else MappingElementId(v) for v in self.transformation_mapping_refs]

        if self.direction is not None and not isinstance(self.direction, FlowDirectionEnum):
            self.direction = FlowDirectionEnum(self.direction)

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
    description: str = None
    contract_ref: Optional[Union[str, DataContractReferenceRegistryId]] = None
    selections: Optional[Union[dict[Union[str, ModelSelectionElementId], Union[dict, "ModelSelection"]], list[Union[dict, "ModelSelection"]]]] = empty_dict()
    compatibility_baseline_ref: Optional[Union[str, URI]] = None
    data_owner_ref: Optional[Union[str, RoleRegistryId]] = None
    data_steward_ref: Optional[Union[str, RoleRegistryId]] = None
    owning_unit_ref: Optional[Union[str, OrganizationUnitRegistryId]] = None
    ownership_inheritance_rule: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, DataModelBindingElementId):
            self.element_id = DataModelBindingElementId(self.element_id)

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

        if self._is_empty(self.description):
            self.MissingRequiredField("description")
        if not isinstance(self.description, str):
            self.description = str(self.description)

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

        if self.ownership_inheritance_rule is not None and not isinstance(self.ownership_inheritance_rule, str):
            self.ownership_inheritance_rule = str(self.ownership_inheritance_rule)

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
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    description: str = None
    selected_entities: Optional[Union[dict[Union[str, SelectedEntityElementId], Union[dict, "SelectedEntity"]], list[Union[dict, "SelectedEntity"]]]] = empty_dict()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, ModelSelectionElementId):
            self.element_id = ModelSelectionElementId(self.element_id)

        if self._is_empty(self.description):
            self.MissingRequiredField("description")
        if not isinstance(self.description, str):
            self.description = str(self.description)

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
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    logical_entity_ref: Union[str, LogicalEntityElementId] = None
    description: str = None
    selected_attributes: Optional[Union[dict[Union[str, SelectedAttributeElementId], Union[dict, "SelectedAttribute"]], list[Union[dict, "SelectedAttribute"]]]] = empty_dict()
    carrier_refs: Optional[Union[Union[str, DataCarrierElementId], list[Union[str, DataCarrierElementId]]]] = empty_list()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, SelectedEntityElementId):
            self.element_id = SelectedEntityElementId(self.element_id)

        if self._is_empty(self.logical_entity_ref):
            self.MissingRequiredField("logical_entity_ref")
        if not isinstance(self.logical_entity_ref, LogicalEntityElementId):
            self.logical_entity_ref = LogicalEntityElementId(self.logical_entity_ref)

        if self._is_empty(self.description):
            self.MissingRequiredField("description")
        if not isinstance(self.description, str):
            self.description = str(self.description)

        self._normalize_inlined_as_list(slot_name="selected_attributes", slot_type=SelectedAttribute, key_name="element_id", keyed=True)

        if not isinstance(self.carrier_refs, list):
            self.carrier_refs = [self.carrier_refs] if self.carrier_refs is not None else []
        self.carrier_refs = [v if isinstance(v, DataCarrierElementId) else DataCarrierElementId(v) for v in self.carrier_refs]

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
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    logical_attribute_ref: Union[str, LogicalAttributeElementId] = None
    description: str = None
    schema_node_refs: Optional[Union[Union[str, URIorCURIE], list[Union[str, URIorCURIE]]]] = empty_list()
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

        if self._is_empty(self.description):
            self.MissingRequiredField("description")
        if not isinstance(self.description, str):
            self.description = str(self.description)

        if not isinstance(self.schema_node_refs, list):
            self.schema_node_refs = [self.schema_node_refs] if self.schema_node_refs is not None else []
        self.schema_node_refs = [v if isinstance(v, URIorCURIE) else URIorCURIE(v) for v in self.schema_node_refs]

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
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    metric_expression: str = None
    aggregation_function: str = None
    description: str = None
    grain_entity_refs: Optional[Union[Union[str, LogicalEntityElementId], list[Union[str, LogicalEntityElementId]]]] = empty_list()
    dimension_attribute_refs: Optional[Union[Union[str, LogicalAttributeElementId], list[Union[str, LogicalAttributeElementId]]]] = empty_list()
    measure_attribute_refs: Optional[Union[Union[str, LogicalAttributeElementId], list[Union[str, LogicalAttributeElementId]]]] = empty_list()
    unit: Optional[str] = None
    filter_expression: Optional[str] = None
    data_owner_ref: Optional[Union[str, RoleRegistryId]] = None
    data_steward_ref: Optional[Union[str, RoleRegistryId]] = None
    owning_unit_ref: Optional[Union[str, OrganizationUnitRegistryId]] = None
    ownership_inheritance_rule: Optional[str] = None
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

        if self._is_empty(self.description):
            self.MissingRequiredField("description")
        if not isinstance(self.description, str):
            self.description = str(self.description)

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

        if self.ownership_inheritance_rule is not None and not isinstance(self.ownership_inheritance_rule, str):
            self.ownership_inheritance_rule = str(self.ownership_inheritance_rule)

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
    lifecycle_status: Union[str, "LifecycleStatusEnum"] = None
    description: str = None
    dimension_attribute_refs: Optional[Union[Union[str, LogicalAttributeElementId], list[Union[str, LogicalAttributeElementId]]]] = empty_list()
    grain_entity_refs: Optional[Union[Union[str, LogicalEntityElementId], list[Union[str, LogicalEntityElementId]]]] = empty_list()

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.element_id):
            self.MissingRequiredField("element_id")
        if not isinstance(self.element_id, DimensionElementId):
            self.element_id = DimensionElementId(self.element_id)

        if self._is_empty(self.description):
            self.MissingRequiredField("description")
        if not isinstance(self.description, str):
            self.description = str(self.description)

        if not isinstance(self.dimension_attribute_refs, list):
            self.dimension_attribute_refs = [self.dimension_attribute_refs] if self.dimension_attribute_refs is not None else []
        self.dimension_attribute_refs = [v if isinstance(v, LogicalAttributeElementId) else LogicalAttributeElementId(v) for v in self.dimension_attribute_refs]

        if not isinstance(self.grain_entity_refs, list):
            self.grain_entity_refs = [self.grain_entity_refs] if self.grain_entity_refs is not None else []
        self.grain_entity_refs = [v if isinstance(v, LogicalEntityElementId) else LogicalEntityElementId(v) for v in self.grain_entity_refs]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class RequirementApplicability(YAMLRoot):
    """
    Область применимости требования (без graph queries): класс цели, профиль и уровень модели.
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = DAMS["RequirementApplicability"]
    class_class_curie: ClassVar[str] = "dams:RequirementApplicability"
    class_name: ClassVar[str] = "RequirementApplicability"
    class_model_uri: ClassVar[URIRef] = DAMS.RequirementApplicability

    applicability_id: Union[str, RequirementApplicabilityApplicabilityId] = None
    applies_target_class: Optional[str] = None
    applies_target_kinds: Optional[Union[str, list[str]]] = empty_list()
    applies_implementation_scope: Optional[Union[str, "ImplementationScopeEnum"]] = None
    applies_dams_model_level: Optional[Union[str, "DAMSModelLevelEnum"]] = None
    applies_implementation_profile: Optional[Union[str, "ImplementationProfileEnum"]] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self._is_empty(self.applicability_id):
            self.MissingRequiredField("applicability_id")
        if not isinstance(self.applicability_id, RequirementApplicabilityApplicabilityId):
            self.applicability_id = RequirementApplicabilityApplicabilityId(self.applicability_id)

        if self.applies_target_class is not None and not isinstance(self.applies_target_class, str):
            self.applies_target_class = str(self.applies_target_class)

        if not isinstance(self.applies_target_kinds, list):
            self.applies_target_kinds = [self.applies_target_kinds] if self.applies_target_kinds is not None else []
        self.applies_target_kinds = [v if isinstance(v, str) else str(v) for v in self.applies_target_kinds]

        if self.applies_implementation_scope is not None and not isinstance(self.applies_implementation_scope, ImplementationScopeEnum):
            self.applies_implementation_scope = ImplementationScopeEnum(self.applies_implementation_scope)

        if self.applies_dams_model_level is not None and not isinstance(self.applies_dams_model_level, DAMSModelLevelEnum):
            self.applies_dams_model_level = DAMSModelLevelEnum(self.applies_dams_model_level)

        if self.applies_implementation_profile is not None and not isinstance(self.applies_implementation_profile, ImplementationProfileEnum):
            self.applies_implementation_profile = ImplementationProfileEnum(self.applies_implementation_profile)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class FormalCheck(YAMLRoot):
    """
    Одна машиночитаемая проверка требования. Kind выровнен с LinkML constraints и DAMS reference/structural
    diagnostics. formal_checks — исполняемое подмножество нормы; исполняется assess (ADR-013).
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
    target_slots: Optional[Union[str, list[str]]] = empty_list()
    target_path: Optional[str] = None
    diagnostic_code: Optional[str] = None
    expression: Optional[str] = None
    remediation: Optional[str] = None

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

        if not isinstance(self.target_slots, list):
            self.target_slots = [self.target_slots] if self.target_slots is not None else []
        self.target_slots = [v if isinstance(v, str) else str(v) for v in self.target_slots]

        if self.target_path is not None and not isinstance(self.target_path, str):
            self.target_path = str(self.target_path)

        if self.diagnostic_code is not None and not isinstance(self.diagnostic_code, str):
            self.diagnostic_code = str(self.diagnostic_code)

        if self.expression is not None and not isinstance(self.expression, str):
            self.expression = str(self.expression)

        if self.remediation is not None and not isinstance(self.remediation, str):
            self.remediation = str(self.remediation)

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
    code: str = None
    requirement_level: Union[str, "RequirementLevelEnum"] = None
    requirement_section: Union[str, "RequirementSectionEnum"] = None
    statement: str = None
    description: str = None
    lifecycle_status: Union[str, "RequirementLifecycleStatus"] = 'draft'
    applies_to: Optional[Union[dict, RequirementApplicability]] = None
    formal_checks: Optional[Union[dict[Union[str, FormalCheckCheckId], Union[dict, FormalCheck]], list[Union[dict, FormalCheck]]]] = empty_dict()
    implementation_status: Optional[Union[str, "RequirementImplementationStatus"]] = None
    superseded_by: Optional[Union[str, SpecificationRequirementElementId]] = None

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

        if self._is_empty(self.description):
            self.MissingRequiredField("description")
        if not isinstance(self.description, str):
            self.description = str(self.description)

        if self._is_empty(self.lifecycle_status):
            self.MissingRequiredField("lifecycle_status")
        if not isinstance(self.lifecycle_status, RequirementLifecycleStatus):
            self.lifecycle_status = RequirementLifecycleStatus(self.lifecycle_status)

        if self.applies_to is not None and not isinstance(self.applies_to, RequirementApplicability):
            self.applies_to = RequirementApplicability(**as_dict(self.applies_to))

        self._normalize_inlined_as_list(slot_name="formal_checks", slot_type=FormalCheck, key_name="check_id", keyed=True)

        if self.implementation_status is not None and not isinstance(self.implementation_status, RequirementImplementationStatus):
            self.implementation_status = RequirementImplementationStatus(self.implementation_status)

        if self.superseded_by is not None and not isinstance(self.superseded_by, SpecificationRequirementElementId):
            self.superseded_by = SpecificationRequirementElementId(self.superseded_by)

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

    draft = LinkMLPermissibleValue(text="draft")
    active = LinkMLPermissibleValue(text="active")
    deprecated = LinkMLPermissibleValue(text="deprecated")
    retired = LinkMLPermissibleValue(text="retired")

    _defn = EnumDefinition(
        name="LifecycleStatusEnum",
    )

class ApprovalStatusEnum(EnumDefinitionImpl):

    proposed = LinkMLPermissibleValue(text="proposed")
    approved = LinkMLPermissibleValue(text="approved")
    rejected = LinkMLPermissibleValue(text="rejected")
    superseded = LinkMLPermissibleValue(text="superseded")

    _defn = EnumDefinition(
        name="ApprovalStatusEnum",
    )

class ModelLevelEnum(EnumDefinitionImpl):

    conceptual = LinkMLPermissibleValue(text="conceptual")
    logical = LinkMLPermissibleValue(text="logical")
    physical = LinkMLPermissibleValue(text="physical")

    _defn = EnumDefinition(
        name="ModelLevelEnum",
    )

class EntityTypeEnum(EnumDefinitionImpl):
    """
    Роль логической сущности в модели решения.
    """
    core = LinkMLPermissibleValue(
        text="core",
        description="Базовая сущность, создаваемая и управляемая решением.")
    derived = LinkMLPermissibleValue(
        text="derived",
        description="""Результат вычисления, агрегации, трансформации или правила; обязательны derivation rule и sources (Wave 2).""")
    reference = LinkMLPermissibleValue(
        text="reference",
        description="Справочная сущность или представление управляемого справочника.")
    projection = LinkMLPermissibleValue(
        text="projection",
        description="""Представление существующей сущности или набора сущностей для конкретного use case (API DTO, read model, витрина).""")
    technical = LinkMLPermissibleValue(
        text="technical",
        description="Не имеет самостоятельного бизнес-смысла вне технической реализации.")

    _defn = EnumDefinition(
        name="EntityTypeEnum",
        description="Роль логической сущности в модели решения.",
    )

class DataClassEnum(EnumDefinitionImpl):
    """
    Класс данных для наследования модельной спецификацией дата-контракта; не совпадает с entity_type.
    """
    reference_data = LinkMLPermissibleValue(
        text="reference_data",
        description="Нормативно-справочная информация (НСИ).")
    master_data = LinkMLPermissibleValue(
        text="master_data",
        description="Мастер-данные.")
    transactional_data = LinkMLPermissibleValue(
        text="transactional_data",
        description="Транзакционные данные.")
    analytical_data = LinkMLPermissibleValue(
        text="analytical_data",
        description="Аналитические или производные наборы данных.")
    metadata = LinkMLPermissibleValue(
        text="metadata",
        description="Метаданные.")
    operational_data = LinkMLPermissibleValue(
        text="operational_data",
        description="""Операционные данные — данные для непосредственного выполнения операций решения, не являющиеся master/reference, transactional событием, analytical результатом или metadata.""")

    _defn = EnumDefinition(
        name="DataClassEnum",
        description="Класс данных для наследования модельной спецификацией дата-контракта; не совпадает с entity_type.",
    )

class BusinessImportanceEnum(EnumDefinitionImpl):
    """
    Важность сущности в модели решения (не criticality бизнес-процесса).
    """
    critical = LinkMLPermissibleValue(text="critical")
    high = LinkMLPermissibleValue(text="high")
    medium = LinkMLPermissibleValue(text="medium")
    low = LinkMLPermissibleValue(text="low")

    _defn = EnumDefinition(
        name="BusinessImportanceEnum",
        description="Важность сущности в модели решения (не criticality бизнес-процесса).",
    )

class BusinessKeyKindEnum(EnumDefinitionImpl):
    """
    Характер бизнес-ключа логической сущности.
    """
    natural = LinkMLPermissibleValue(
        text="natural",
        description="Устойчивый бизнес-идентификатор, независимый от технической реализации.")
    composite = LinkMLPermissibleValue(
        text="composite",
        description="Комбинация нескольких бизнес-атрибутов, уникальная в контексте.")
    external = LinkMLPermissibleValue(
        text="external",
        description="Идентификатор внешней системы, реестра или контрагента.")
    local = LinkMLPermissibleValue(
        text="local",
        description="Идентификатор, уникальный только в границе ИТ-решения или контекста.")
    surrogate = LinkMLPermissibleValue(
        text="surrogate",
        description="Технический ключ реализации; не заменяет identity_rule.")
    derived = LinkMLPermissibleValue(
        text="derived",
        description="Идентификатор, вычисляемый из других атрибутов по документированному правилу.")

    _defn = EnumDefinition(
        name="BusinessKeyKindEnum",
        description="Характер бизнес-ключа логической сущности.",
    )

class ConceptualAlignmentStatusEnum(EnumDefinitionImpl):
    """
    Статус выравнивания логической сущности с корпоративным концептуальным уровнем.
    """
    aligned = LinkMLPermissibleValue(
        text="aligned",
        description="Есть ссылка на одну или несколько концептуальных сущностей.")
    pending = LinkMLPermissibleValue(
        text="pending",
        description="Связь должна быть установлена, но пока не утверждена; rationale обязателен.")

    _defn = EnumDefinition(
        name="ConceptualAlignmentStatusEnum",
        description="Статус выравнивания логической сущности с корпоративным концептуальным уровнем.",
    )

    @classmethod
    def _addvals(cls):
        setattr(cls, "local-only",
            LinkMLPermissibleValue(
                text="local-only",
                description="""Бизнес-смысл только в контексте данного решения; корпоративный аналог сейчас не требуется; rationale обязателен."""))
        setattr(cls, "not-applicable",
            LinkMLPermissibleValue(
                text="not-applicable",
                description="""Сущность техническая/служебная и не относится к conceptual layer; допустимо только при entity_type technical."""))

class DefinitionScopeKindEnum(EnumDefinitionImpl):
    """
    Kind of scope for a ScopedDefinition (ADR-025). v1 supports system only; enum is intentionally extensible.
    """
    system = LinkMLPermissibleValue(
        text="system",
        description="Definition applies within one ITSystem of the solution.")

    _defn = EnumDefinition(
        name="DefinitionScopeKindEnum",
        description="""Kind of scope for a ScopedDefinition (ADR-025). v1 supports system only; enum is intentionally extensible.""",
    )

class ScopedDefinitionRelationEnum(EnumDefinitionImpl):
    """
    How a scoped definition relates to the element's reference definition (ADR-025).
    """
    refines = LinkMLPermissibleValue(
        text="refines",
        description="Clarifies the reference definition without changing extension.")
    narrows = LinkMLPermissibleValue(
        text="narrows",
        description="Restricts the meaning to a subset in this scope.")
    alternative = LinkMLPermissibleValue(
        text="alternative",
        description="Parallel wording for the same concept in this scope.")
    replaces = LinkMLPermissibleValue(
        text="replaces",
        description="Scope-local replacement; does not change the reference outside scope.")

    _defn = EnumDefinition(
        name="ScopedDefinitionRelationEnum",
        description="""How a scoped definition relates to the element's reference definition (ADR-025).""",
    )

class EntityTierEnum(EnumDefinitionImpl):
    """
    Structural independence of a ConceptualEntity (ADR-026). Orthogonal to entity_type, data_class, and
    business_importance.
    """
    primary = LinkMLPermissibleValue(
        text="primary",
        description="""Existence does not depend on other conceptual entities (FK presence alone does not make an entity dependent).""")
    dependent = LinkMLPermissibleValue(
        text="dependent",
        description="""Cannot exist without owner entity/entities listed in depends_on_refs.""")

    _defn = EnumDefinition(
        name="EntityTierEnum",
        description="""Structural independence of a ConceptualEntity (ADR-026). Orthogonal to entity_type, data_class, and business_importance.""",
    )

class DependencyKindEnum(EnumDefinitionImpl):
    """
    Kind of structural dependency for a dependent ConceptualEntity (ADR-026).
    """
    characteristic = LinkMLPermissibleValue(
        text="characteristic",
        description="Part or detail of an owning entity (owner key in identity).")
    associative = LinkMLPermissibleValue(
        text="associative",
        description="Resolves an M:N association between owner entities.")

    _defn = EnumDefinition(
        name="DependencyKindEnum",
        description="""Kind of structural dependency for a dependent ConceptualEntity (ADR-026).""",
    )

class GenesisKindEnum(EnumDefinitionImpl):
    """
    Whether a ConceptualEntity is aligned to an external class/term or is native to MOEX (ADR-026).
    """
    external = LinkMLPermissibleValue(
        text="external",
        description="""Aligns to one or more ontology classes or external-specification terms (corporate architecture, business models, API/data standards).""")
    native = LinkMLPermissibleValue(
        text="native",
        description="Modelled in MOEX without external parent classes.")

    _defn = EnumDefinition(
        name="GenesisKindEnum",
        description="""Whether a ConceptualEntity is aligned to an external class/term or is native to MOEX (ADR-026).""",
    )

class ExternalMatchKindEnum(EnumDefinitionImpl):
    """
    Strength of ConceptualEntity ↔ external class alignment (ADR-026). Mirrors SKOS mapping relations plus
    owl:equivalentClass; used for definition inheritance (exact/equivalent only).
    """
    exact = LinkMLPermissibleValue(
        text="exact",
        description="skos:exactMatch — substitutable; definition may inherit.")
    equivalent = LinkMLPermissibleValue(
        text="equivalent",
        description="owl:equivalentClass — substitutable; definition may inherit.")
    close = LinkMLPermissibleValue(
        text="close",
        description="skos:closeMatch — not substitutable; own description required.")
    broad = LinkMLPermissibleValue(
        text="broad",
        description="skos:broadMatch — external is broader; own description required.")
    narrow = LinkMLPermissibleValue(
        text="narrow",
        description="skos:narrowMatch — external is narrower; own description required.")

    _defn = EnumDefinition(
        name="ExternalMatchKindEnum",
        description="""Strength of ConceptualEntity ↔ external class alignment (ADR-026). Mirrors SKOS mapping relations plus owl:equivalentClass; used for definition inheritance (exact/equivalent only).""",
    )

class ExternalSourceKindEnum(EnumDefinitionImpl):
    """
    Kind of external source for a ConceptualEntity alignment (ADR-026). Aligned with ExternalSpecificationKind where
    values overlap.
    """
    ontology = LinkMLPermissibleValue(text="ontology")
    other = LinkMLPermissibleValue(text="other")

    _defn = EnumDefinition(
        name="ExternalSourceKindEnum",
        description="""Kind of external source for a ConceptualEntity alignment (ADR-026). Aligned with ExternalSpecificationKind where values overlap.""",
    )

    @classmethod
    def _addvals(cls):
        setattr(cls, "corporate-architecture",
            LinkMLPermissibleValue(text="corporate-architecture"))
        setattr(cls, "business-model",
            LinkMLPermissibleValue(text="business-model"))
        setattr(cls, "api-spec",
            LinkMLPermissibleValue(text="api-spec"))

class TermDirectionEnum(EnumDefinitionImpl):
    """
    Which side of a RelationTerm a Relationship assertion uses (ADR-026).
    """
    forward = LinkMLPermissibleValue(
        text="forward",
        description="Assertion reads with forward_label (source → target).")
    inverse = LinkMLPermissibleValue(
        text="inverse",
        description="Assertion reads with inverse_label (source → target uses inverse wording).")

    _defn = EnumDefinition(
        name="TermDirectionEnum",
        description="""Which side of a RelationTerm a Relationship assertion uses (ADR-026).""",
    )

class MappingCoverageStatusEnum(EnumDefinitionImpl):
    """
    Статус покрытия элемента mapping’ом на соседнем уровне модели (logical ↔ physical). Не статус самой логической
    модели.
    """
    mapped = LinkMLPermissibleValue(
        text="mapped",
        description="Есть формальное mapping.")
    derived = LinkMLPermissibleValue(
        text="derived",
        description="Значение выводится из источников по documented expression.")
    planned = LinkMLPermissibleValue(
        text="planned",
        description="""Физическая реализация или mapping ещё не введены. Требует mapping_rationale; не постоянный обход для active артефактов.""")
    inherited = LinkMLPermissibleValue(
        text="inherited",
        description="Mapping наследуется/делегируется из родительского элемента.")

    _defn = EnumDefinition(
        name="MappingCoverageStatusEnum",
        description="""Статус покрытия элемента mapping’ом на соседнем уровне модели (logical ↔ physical). Не статус самой логической модели.""",
    )

    @classmethod
    def _addvals(cls):
        setattr(cls, "technical-only",
            LinkMLPermissibleValue(
                text="technical-only",
                description="Поле/объект имеет только техническое назначение."))
        setattr(cls, "not-applicable",
            LinkMLPermissibleValue(
                text="not-applicable",
                description="Mapping неприменим по характеру элемента."))

class RelationshipKindEnum(EnumDefinitionImpl):
    """
    Тип логической связи (Wave 2).
    """
    association = LinkMLPermissibleValue(text="association")
    composition = LinkMLPermissibleValue(text="composition")
    aggregation = LinkMLPermissibleValue(text="aggregation")
    specialization = LinkMLPermissibleValue(text="specialization")
    reference = LinkMLPermissibleValue(text="reference")
    derivation = LinkMLPermissibleValue(text="derivation")
    realization = LinkMLPermissibleValue(text="realization")
    lineage = LinkMLPermissibleValue(text="lineage")
    event_participation = LinkMLPermissibleValue(text="event_participation")

    _defn = EnumDefinition(
        name="RelationshipKindEnum",
        description="Тип логической связи (Wave 2).",
    )

class SecurityClassificationEnum(EnumDefinitionImpl):
    """
    Режим защиты данных (Wave 2); ортогонален governance_classification.
    """
    internal = LinkMLPermissibleValue(text="internal")
    confidential = LinkMLPermissibleValue(text="confidential")
    restricted = LinkMLPermissibleValue(text="restricted")

    _defn = EnumDefinition(
        name="SecurityClassificationEnum",
        description="Режим защиты данных (Wave 2); ортогонален governance_classification.",
    )

class GovernanceClassificationEnum(EnumDefinitionImpl):
    """
    Базовая шкала ограничения доступа; специальные виды тайны задаются отдельными терминами классификации.
    """
    public = LinkMLPermissibleValue(text="public")
    internal = LinkMLPermissibleValue(text="internal")
    confidential = LinkMLPermissibleValue(text="confidential")
    restricted = LinkMLPermissibleValue(text="restricted")

    _defn = EnumDefinition(
        name="GovernanceClassificationEnum",
        description="""Базовая шкала ограничения доступа; специальные виды тайны задаются отдельными терминами классификации.""",
    )

class LogicalDataTypeEnum(EnumDefinitionImpl):

    string = LinkMLPermissibleValue(text="string")
    integer = LinkMLPermissibleValue(text="integer")
    decimal = LinkMLPermissibleValue(text="decimal")
    boolean = LinkMLPermissibleValue(text="boolean")
    date = LinkMLPermissibleValue(text="date")
    datetime = LinkMLPermissibleValue(text="datetime")
    time = LinkMLPermissibleValue(text="time")
    binary = LinkMLPermissibleValue(text="binary")
    identifier = LinkMLPermissibleValue(text="identifier")
    uri = LinkMLPermissibleValue(text="uri")
    object = LinkMLPermissibleValue(text="object")

    _defn = EnumDefinition(
        name="LogicalDataTypeEnum",
    )

class FlowDirectionEnum(EnumDefinitionImpl):

    inbound = LinkMLPermissibleValue(text="inbound")
    outbound = LinkMLPermissibleValue(text="outbound")
    internal = LinkMLPermissibleValue(text="internal")
    bidirectional = LinkMLPermissibleValue(text="bidirectional")

    _defn = EnumDefinition(
        name="FlowDirectionEnum",
    )

class SolutionDataRoleEnum(EnumDefinitionImpl):

    producer = LinkMLPermissibleValue(text="producer")
    consumer = LinkMLPermissibleValue(text="consumer")
    intermediary = LinkMLPermissibleValue(text="intermediary")

    _defn = EnumDefinition(
        name="SolutionDataRoleEnum",
    )

class IntegrationChannelEnum(EnumDefinitionImpl):

    api = LinkMLPermissibleValue(text="api")
    queue = LinkMLPermissibleValue(text="queue")
    database = LinkMLPermissibleValue(text="database")
    file = LinkMLPermissibleValue(text="file")
    other = LinkMLPermissibleValue(text="other")

    _defn = EnumDefinition(
        name="IntegrationChannelEnum",
    )

class IntegrationClassEnum(EnumDefinitionImpl):

    EAP = LinkMLPermissibleValue(text="EAP")
    EDA = LinkMLPermissibleValue(text="EDA")

    _defn = EnumDefinition(
        name="IntegrationClassEnum",
    )

class IntegrationLevelEnum(EnumDefinitionImpl):

    intraplatform = LinkMLPermissibleValue(text="intraplatform")
    interplatform = LinkMLPermissibleValue(text="interplatform")

    _defn = EnumDefinition(
        name="IntegrationLevelEnum",
    )

class MappingTypeEnum(EnumDefinitionImpl):
    """
    Kind of Mapping assertion. realizes = solution element → enterprise conceptual; entity_physical = DataCarrier ↔
    LogicalEntity; field_mapping = mapsTo (SchemaNode ↔ LogicalAttribute); aligns_with = enterprise conceptual ↔
    external term. Do not use Mapping for SpecImpl implements (that is conforms_to / publication implements).
    """
    semantic_equivalence = LinkMLPermissibleValue(text="semantic_equivalence")
    specialization = LinkMLPermissibleValue(text="specialization")
    implementation = LinkMLPermissibleValue(text="implementation")
    entity_physical = LinkMLPermissibleValue(
        text="entity_physical",
        description="""Explicit entity-level link between DataCarrier and LogicalEntity (PDM-003). Do not infer from field_mapping alone.""")
    field_mapping = LinkMLPermissibleValue(
        text="field_mapping",
        description="""mapsTo between SchemaNode (structure_id#local_key) and LogicalAttribute (ADR-038).""")
    transformation = LinkMLPermissibleValue(text="transformation")
    aggregation = LinkMLPermissibleValue(text="aggregation")
    derivation = LinkMLPermissibleValue(text="derivation")
    realizes = LinkMLPermissibleValue(
        text="realizes",
        description="Solution logical/concept realizes an enterprise conceptual entity.")
    aligns_with = LinkMLPermissibleValue(
        text="aligns_with",
        description="Enterprise conceptual aligns with an external reference term.")

    _defn = EnumDefinition(
        name="MappingTypeEnum",
        description="""Kind of Mapping assertion. realizes = solution element → enterprise conceptual; entity_physical = DataCarrier ↔ LogicalEntity; field_mapping = mapsTo (SchemaNode ↔ LogicalAttribute); aligns_with = enterprise conceptual ↔ external term. Do not use Mapping for SpecImpl implements (that is conforms_to / publication implements).""",
    )

class ImplementationProfileEnum(EnumDefinitionImpl):
    """
    DAMS-side mirror of kernel ImplementationProfile for ModelPackage metadata. Package-level dams_model_level applies
    only to dams-data-model.
    """
    other = LinkMLPermissibleValue(text="other")

    _defn = EnumDefinition(
        name="ImplementationProfileEnum",
        description="""DAMS-side mirror of kernel ImplementationProfile for ModelPackage metadata. Package-level dams_model_level applies only to dams-data-model.""",
    )

    @classmethod
    def _addvals(cls):
        setattr(cls, "dams-data-model",
            LinkMLPermissibleValue(
                text="dams-data-model",
                description="MOEX DAMS corporate data-model implementation."))
        setattr(cls, "ontology-application",
            LinkMLPermissibleValue(
                text="ontology-application",
                description="Not a DAMS model Impl — ontology application profile."))
        setattr(cls, "api-specification",
            LinkMLPermissibleValue(text="api-specification"))
        setattr(cls, "data-contract",
            LinkMLPermissibleValue(text="data-contract"))

class DAMSModelLevelEnum(EnumDefinitionImpl):
    """
    Package-level DAMS model layer (ADR-021). Distinct from ModelLevelEnum (element conceptual/logical/physical). No
    domain-logical value.
    """
    solution = LinkMLPermissibleValue(
        text="solution",
        description="IT-solution model with local logical/physical facets.")

    _defn = EnumDefinition(
        name="DAMSModelLevelEnum",
        description="""Package-level DAMS model layer (ADR-021). Distinct from ModelLevelEnum (element conceptual/logical/physical). No domain-logical value.""",
    )

    @classmethod
    def _addvals(cls):
        setattr(cls, "enterprise-conceptual",
            LinkMLPermissibleValue(
                text="enterprise-conceptual",
                description="Enterprise corporate conceptual model (solution-independent)."))

class ImplementationScopeEnum(EnumDefinitionImpl):

    enterprise = LinkMLPermissibleValue(
        text="enterprise",
        description="Enterprise-wide scope (no solution_ref).")
    solution = LinkMLPermissibleValue(
        text="solution",
        description="Scoped to a specific IT solution.")

    _defn = EnumDefinition(
        name="ImplementationScopeEnum",
    )

class MappingCardinalityEnum(EnumDefinitionImpl):

    one_to_one = LinkMLPermissibleValue(text="one_to_one")
    one_to_many = LinkMLPermissibleValue(text="one_to_many")
    many_to_one = LinkMLPermissibleValue(text="many_to_one")
    many_to_many = LinkMLPermissibleValue(text="many_to_many")

    _defn = EnumDefinition(
        name="MappingCardinalityEnum",
    )

class CompatibilityModeEnum(EnumDefinitionImpl):

    backward = LinkMLPermissibleValue(text="backward")
    forward = LinkMLPermissibleValue(text="forward")
    full = LinkMLPermissibleValue(text="full")
    none = LinkMLPermissibleValue(text="none")

    _defn = EnumDefinition(
        name="CompatibilityModeEnum",
    )

class SpecificationKindEnum(EnumDefinitionImpl):

    integration = LinkMLPermissibleValue(text="integration")
    data_model = LinkMLPermissibleValue(text="data_model")
    data_quality = LinkMLPermissibleValue(text="data_quality")

    _defn = EnumDefinition(
        name="SpecificationKindEnum",
    )

class EnforcementResultEnum(EnumDefinitionImpl):

    warn = LinkMLPermissibleValue(text="warn")
    fail = LinkMLPermissibleValue(text="fail")
    not_applicable = LinkMLPermissibleValue(text="not_applicable")

    _defn = EnumDefinition(
        name="EnforcementResultEnum",
    )

    @classmethod
    def _addvals(cls):
        setattr(cls, "pass",
            LinkMLPermissibleValue(text="pass"))

class RequirementLevelEnum(EnumDefinitionImpl):
    """
    Уровень применения требования к спецификации.
    """
    conceptual_model = LinkMLPermissibleValue(
        text="conceptual_model",
        description="Концептуальная модель")
    it_solution = LinkMLPermissibleValue(
        text="it_solution",
        description="ИТ-решение")
    it_system = LinkMLPermissibleValue(
        text="it_system",
        description="ИТ-система")

    _defn = EnumDefinition(
        name="RequirementLevelEnum",
        description="Уровень применения требования к спецификации.",
    )

class RequirementLifecycleStatus(EnumDefinitionImpl):
    """
    Статус жизненного цикла нормативного требования (SpecificationRequirement). Не заменяет ApprovalStatusEnum
    (согласование provenance у других элементов).
    """
    draft = LinkMLPermissibleValue(
        text="draft",
        description="Черновик, формулируется")
    proposed = LinkMLPermissibleValue(
        text="proposed",
        description="Вынесено на согласование")
    approved = LinkMLPermissibleValue(
        text="approved",
        description="Принято как норма")
    rejected = LinkMLPermissibleValue(
        text="rejected",
        description="Отклонено")
    deprecated = LinkMLPermissibleValue(
        text="deprecated",
        description="Больше не актуально, замены нет")
    superseded = LinkMLPermissibleValue(
        text="superseded",
        description="Заменено другим требованием")

    _defn = EnumDefinition(
        name="RequirementLifecycleStatus",
        description="""Статус жизненного цикла нормативного требования (SpecificationRequirement). Не заменяет ApprovalStatusEnum (согласование provenance у других элементов).""",
    )

class RequirementImplementationStatus(EnumDefinitionImpl):
    """
    Статус реализации утверждённого требования. Осмысленно при lifecycle_status=approved; не заменяет
    ApprovalStatusEnum.
    """
    not_started = LinkMLPermissibleValue(
        text="not_started",
        description="Не начато")
    in_progress = LinkMLPermissibleValue(
        text="in_progress",
        description="Реализуется")
    implemented = LinkMLPermissibleValue(
        text="implemented",
        description="Реализовано")
    verified = LinkMLPermissibleValue(
        text="verified",
        description="Проверено")

    _defn = EnumDefinition(
        name="RequirementImplementationStatus",
        description="""Статус реализации утверждённого требования. Осмысленно при lifecycle_status=approved; не заменяет ApprovalStatusEnum.""",
    )

class RequirementSectionEnum(EnumDefinitionImpl):
    """
    Раздел каталога требований (трёхбуквенный код в code).
    """
    LDM = LinkMLPermissibleValue(
        text="LDM",
        description="Логическая модель")
    PDM = LinkMLPermissibleValue(
        text="PDM",
        description="Физическая модель")
    REF = LinkMLPermissibleValue(
        text="REF",
        description="Связи сущностей")
    ATR = LinkMLPermissibleValue(
        text="ATR",
        description="Атрибуты")
    FLW = LinkMLPermissibleValue(
        text="FLW",
        description="Потоки данных")
    CLS = LinkMLPermissibleValue(
        text="CLS",
        description="Классификация данных")
    GEN = LinkMLPermissibleValue(
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
    slot_required = LinkMLPermissibleValue(text="slot_required")
    slot_min_cardinality = LinkMLPermissibleValue(text="slot_min_cardinality")
    ref_resolves = LinkMLPermissibleValue(text="ref_resolves")
    key_subset = LinkMLPermissibleValue(text="key_subset")
    at_least_one_slots = LinkMLPermissibleValue(
        text="at_least_one_slots",
        description="Хотя бы один из target_slots заполнен (override обоих допустим).")
    definition_resolvable = LinkMLPermissibleValue(
        text="definition_resolvable",
        description="""Effective definition must resolve (ADR-025): own description, definition_source_ref, or single conceptual_entity_refs inheritance.""")
    conditional_branch = LinkMLPermissibleValue(
        text="conditional_branch",
        description="""Фиксированный шаблон (имя в expression): status→slots, allowlist kinds, planned guard, semantic inclusion и т.п. Без произвольного mini-language.""")
    custom = LinkMLPermissibleValue(text="custom")

    _defn = EnumDefinition(
        name="FormalCheckKindEnum",
        description="Вид формальной проверки в нотации, близкой к LinkML constraints.",
    )

class CheckSeverityEnum(EnumDefinitionImpl):

    error = LinkMLPermissibleValue(text="error")
    warning = LinkMLPermissibleValue(text="warning")

    _defn = EnumDefinition(
        name="CheckSeverityEnum",
    )

class ConceptualDomainKindEnum(EnumDefinitionImpl):
    """
    Вид концептуального домена (ISO 11179 Conceptual Domain).
    """
    enumerated = LinkMLPermissibleValue(
        text="enumerated",
        description="Домен с явным набором ValueMeaning или внешней concept scheme.")
    described = LinkMLPermissibleValue(
        text="described",
        description="Домен, заданный описанием без перечисления смыслов.")

    _defn = EnumDefinition(
        name="ConceptualDomainKindEnum",
        description="Вид концептуального домена (ISO 11179 Conceptual Domain).",
    )

class ValueDomainKindEnum(EnumDefinitionImpl):
    """
    Вид домена представления значений (ISO 11179 Value Domain).
    """
    enumerated = LinkMLPermissibleValue(
        text="enumerated",
        description="Явный список PermissibleValue.")
    described = LinkMLPermissibleValue(
        text="described",
        description="Описание через формат, min/max, единицу.")
    reference_set = LinkMLPermissibleValue(
        text="reference_set",
        description="Внешний или динамический набор значений.")

    _defn = EnumDefinition(
        name="ValueDomainKindEnum",
        description="Вид домена представления значений (ISO 11179 Value Domain).",
    )

class TypeFamilyEnum(EnumDefinitionImpl):
    """
    Семейство корпоративного DataType.
    """
    boolean = LinkMLPermissibleValue(text="boolean")
    integer = LinkMLPermissibleValue(text="integer")
    decimal = LinkMLPermissibleValue(text="decimal")
    float = LinkMLPermissibleValue(text="float")
    string = LinkMLPermissibleValue(text="string")
    binary = LinkMLPermissibleValue(text="binary")
    date = LinkMLPermissibleValue(text="date")
    time = LinkMLPermissibleValue(text="time")
    datetime = LinkMLPermissibleValue(text="datetime")
    duration = LinkMLPermissibleValue(text="duration")
    identifier = LinkMLPermissibleValue(text="identifier")
    uri = LinkMLPermissibleValue(text="uri")
    object = LinkMLPermissibleValue(text="object")
    array = LinkMLPermissibleValue(text="array")
    other = LinkMLPermissibleValue(text="other")

    _defn = EnumDefinition(
        name="TypeFamilyEnum",
        description="Семейство корпоративного DataType.",
    )

class TimezonePolicyEnum(EnumDefinitionImpl):
    """
    Политика часового пояса для временных DataType.
    """
    none = LinkMLPermissibleValue(text="none")
    utc = LinkMLPermissibleValue(text="utc")
    with_offset = LinkMLPermissibleValue(text="with_offset")
    local = LinkMLPermissibleValue(text="local")

    _defn = EnumDefinition(
        name="TimezonePolicyEnum",
        description="Политика часового пояса для временных DataType.",
    )

class LossinessEnum(EnumDefinitionImpl):
    """
    Оценка потери точности NativeTypeBinding.
    """
    lossless = LinkMLPermissibleValue(text="lossless")
    lossy = LinkMLPermissibleValue(text="lossy")
    unknown = LinkMLPermissibleValue(text="unknown")

    _defn = EnumDefinition(
        name="LossinessEnum",
        description="Оценка потери точности NativeTypeBinding.",
    )

class SignificanceBasisEnum(EnumDefinitionImpl):
    """
    Основание существования ConceptualProperty в КМД (вариант B).
    """
    identifying = LinkMLPermissibleValue(
        text="identifying",
        description="Входит в бизнес-ключ сущности.")
    externally_aligned = LinkMLPermissibleValue(
        text="externally_aligned",
        description="Выравнивается с внешним термином (FIBO, ISO, API).")
    cross_solution = LinkMLPermissibleValue(
        text="cross_solution",
        description="Используется в двух и более решениях.")
    regulatory = LinkMLPermissibleValue(
        text="regulatory",
        description="Упомянуто в нормативном требовании или отчётности.")
    critical_data = LinkMLPermissibleValue(
        text="critical_data",
        description="Критичный элемент данных (CDE), поднятый с логического уровня.")
    governance_anchor = LinkMLPermissibleValue(
        text="governance_anchor",
        description="Привязаны политика или классификация предприятия.")
    explicit_decision = LinkMLPermissibleValue(
        text="explicit_decision",
        description="Решение архитектурного комитета (нужен significance_rationale).")

    _defn = EnumDefinition(
        name="SignificanceBasisEnum",
        description="Основание существования ConceptualProperty в КМД (вариант B).",
    )

class PropertyKindEnum(EnumDefinitionImpl):
    """
    Вид концептуального свойства.
    """
    descriptive = LinkMLPermissibleValue(text="descriptive")
    identifying = LinkMLPermissibleValue(text="identifying")
    relational = LinkMLPermissibleValue(text="relational")
    measure = LinkMLPermissibleValue(text="measure")
    temporal = LinkMLPermissibleValue(text="temporal")
    status = LinkMLPermissibleValue(text="status")

    _defn = EnumDefinition(
        name="PropertyKindEnum",
        description="Вид концептуального свойства.",
    )

class SchemaFormatEnum(EnumDefinitionImpl):
    """
    Формат схемы DataStructure (стартовый набор; перенос в реестр — отдельно).
    """
    json_schema = LinkMLPermissibleValue(text="json_schema")
    avro = LinkMLPermissibleValue(text="avro")
    protobuf = LinkMLPermissibleValue(text="protobuf")
    xml_schema = LinkMLPermissibleValue(text="xml_schema")
    relational = LinkMLPermissibleValue(text="relational")
    openapi_schema = LinkMLPermissibleValue(text="openapi_schema")
    other = LinkMLPermissibleValue(text="other")

    _defn = EnumDefinition(
        name="SchemaFormatEnum",
        description="""Формат схемы DataStructure (стартовый набор; перенос в реестр — отдельно).""",
    )

class SchemaNodeKindEnum(EnumDefinitionImpl):
    """
    Вид узла SchemaNode.
    """
    scalar = LinkMLPermissibleValue(text="scalar")
    object = LinkMLPermissibleValue(text="object")
    array = LinkMLPermissibleValue(text="array")
    map = LinkMLPermissibleValue(text="map")
    union = LinkMLPermissibleValue(text="union")
    enum = LinkMLPermissibleValue(text="enum")
    reference = LinkMLPermissibleValue(text="reference")

    _defn = EnumDefinition(
        name="SchemaNodeKindEnum",
        description="Вид узла SchemaNode.",
    )

class EnvelopeKindEnum(EnumDefinitionImpl):
    """
    Вид конверта сообщения (Message.envelope_kind).
    """
    none = LinkMLPermissibleValue(text="none")
    cloudevents = LinkMLPermissibleValue(text="cloudevents")
    custom = LinkMLPermissibleValue(text="custom")

    _defn = EnumDefinition(
        name="EnvelopeKindEnum",
        description="Вид конверта сообщения (Message.envelope_kind).",
    )

class DataCarrierKindEnum(EnumDefinitionImpl):

    relational_table = LinkMLPermissibleValue(text="relational_table")
    relational_view = LinkMLPermissibleValue(text="relational_view")
    file = LinkMLPermissibleValue(text="file")
    dataset = LinkMLPermissibleValue(text="dataset")
    stream_topic = LinkMLPermissibleValue(text="stream_topic")
    stream_queue = LinkMLPermissibleValue(text="stream_queue")
    in_memory = LinkMLPermissibleValue(text="in_memory")
    api_resource = LinkMLPermissibleValue(text="api_resource")
    other = LinkMLPermissibleValue(text="other")

    _defn = EnumDefinition(
        name="DataCarrierKindEnum",
    )

class AccessPointKindEnum(EnumDefinitionImpl):

    interface = LinkMLPermissibleValue(text="interface")
    operation = LinkMLPermissibleValue(text="operation")
    channel = LinkMLPermissibleValue(text="channel")

    _defn = EnumDefinition(
        name="AccessPointKindEnum",
    )

class DataContainerKindEnum(EnumDefinitionImpl):

    database = LinkMLPermissibleValue(text="database")
    schema = LinkMLPermissibleValue(text="schema")
    bucket = LinkMLPermissibleValue(text="bucket")
    broker = LinkMLPermissibleValue(text="broker")
    directory = LinkMLPermissibleValue(text="directory")
    cluster = LinkMLPermissibleValue(text="cluster")

    _defn = EnumDefinition(
        name="DataContainerKindEnum",
    )

class ExecutionAssetKindEnum(EnumDefinitionImpl):

    pipeline = LinkMLPermissibleValue(text="pipeline")
    job = LinkMLPermissibleValue(text="job")

    _defn = EnumDefinition(
        name="ExecutionAssetKindEnum",
    )

class LineageRoleEnum(EnumDefinitionImpl):

    source = LinkMLPermissibleValue(text="source")
    sink = LinkMLPermissibleValue(text="sink")
    intermediate = LinkMLPermissibleValue(text="intermediate")
    none = LinkMLPermissibleValue(text="none")

    _defn = EnumDefinition(
        name="LineageRoleEnum",
    )

class ContainmentKindEnum(EnumDefinitionImpl):

    composite = LinkMLPermissibleValue(text="composite")
    partitioned = LinkMLPermissibleValue(text="partitioned")
    hierarchical = LinkMLPermissibleValue(text="hierarchical")

    _defn = EnumDefinition(
        name="ContainmentKindEnum",
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

slots.element_id = Slot(uri=DAMS.element_id, name="element_id", curie=DAMS.curie('element_id'),
                   model_uri=DAMS.element_id, domain=None, range=URIRef)

slots.name = Slot(uri=DAMS.name, name="name", curie=DAMS.curie('name'),
                   model_uri=DAMS.name, domain=None, range=str)

slots.title = Slot(uri=DAMS.title, name="title", curie=DAMS.curie('title'),
                   model_uri=DAMS.title, domain=None, range=Optional[str])

slots.description = Slot(uri=DAMS.description, name="description", curie=DAMS.curie('description'),
                   model_uri=DAMS.description, domain=None, range=Optional[str])

slots.aliases = Slot(uri=DAMS.aliases, name="aliases", curie=DAMS.curie('aliases'),
                   model_uri=DAMS.aliases, domain=None, range=Optional[Union[str, list[str]]])

slots.glossary_term_refs = Slot(uri=DAMS.glossary_term_refs, name="glossary_term_refs", curie=DAMS.curie('glossary_term_refs'),
                   model_uri=DAMS.glossary_term_refs, domain=None, range=Optional[Union[Union[str, GlossaryTermRegistryId], list[Union[str, GlossaryTermRegistryId]]]])

slots.tags = Slot(uri=DAMS.tags, name="tags", curie=DAMS.curie('tags'),
                   model_uri=DAMS.tags, domain=None, range=Optional[Union[str, list[str]]])

slots.valid_from = Slot(uri=DAMS.valid_from, name="valid_from", curie=DAMS.curie('valid_from'),
                   model_uri=DAMS.valid_from, domain=None, range=Optional[Union[str, XSDDateTime]])

slots.valid_to = Slot(uri=DAMS.valid_to, name="valid_to", curie=DAMS.curie('valid_to'),
                   model_uri=DAMS.valid_to, domain=None, range=Optional[Union[str, XSDDateTime]])

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

slots.deprecated_by_ref = Slot(uri=DAMS.deprecated_by_ref, name="deprecated_by_ref", curie=DAMS.curie('deprecated_by_ref'),
                   model_uri=DAMS.deprecated_by_ref, domain=None, range=Optional[Union[str, URIorCURIE]])

slots.data_owner_ref = Slot(uri=DAMS.data_owner_ref, name="data_owner_ref", curie=DAMS.curie('data_owner_ref'),
                   model_uri=DAMS.data_owner_ref, domain=None, range=Optional[Union[str, RoleRegistryId]])

slots.data_steward_ref = Slot(uri=DAMS.data_steward_ref, name="data_steward_ref", curie=DAMS.curie('data_steward_ref'),
                   model_uri=DAMS.data_steward_ref, domain=None, range=Optional[Union[str, RoleRegistryId]])

slots.owning_unit_ref = Slot(uri=DAMS.owning_unit_ref, name="owning_unit_ref", curie=DAMS.curie('owning_unit_ref'),
                   model_uri=DAMS.owning_unit_ref, domain=None, range=Optional[Union[str, OrganizationUnitRegistryId]])

slots.ownership_inheritance_rule = Slot(uri=DAMS.ownership_inheritance_rule, name="ownership_inheritance_rule", curie=DAMS.curie('ownership_inheritance_rule'),
                   model_uri=DAMS.ownership_inheritance_rule, domain=None, range=Optional[str])

slots.entity_type = Slot(uri=DAMS.entity_type, name="entity_type", curie=DAMS.curie('entity_type'),
                   model_uri=DAMS.entity_type, domain=None, range=Optional[Union[str, "EntityTypeEnum"]])

slots.data_class = Slot(uri=DAMS.data_class, name="data_class", curie=DAMS.curie('data_class'),
                   model_uri=DAMS.data_class, domain=None, range=Optional[Union[str, "DataClassEnum"]])

slots.business_importance = Slot(uri=DAMS.business_importance, name="business_importance", curie=DAMS.curie('business_importance'),
                   model_uri=DAMS.business_importance, domain=None, range=Optional[Union[str, "BusinessImportanceEnum"]])

slots.governance_classification = Slot(uri=DAMS.governance_classification, name="governance_classification", curie=DAMS.curie('governance_classification'),
                   model_uri=DAMS.governance_classification, domain=None, range=Optional[Union[str, "GovernanceClassificationEnum"]])

slots.security_classification = Slot(uri=DAMS.security_classification, name="security_classification", curie=DAMS.curie('security_classification'),
                   model_uri=DAMS.security_classification, domain=None, range=Optional[Union[str, "SecurityClassificationEnum"]])

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

slots.definition_source_ref = Slot(uri=DAMS.definition_source_ref, name="definition_source_ref", curie=DAMS.curie('definition_source_ref'),
                   model_uri=DAMS.definition_source_ref, domain=None, range=Optional[Union[str, URIorCURIE]])

slots.definition_rationale = Slot(uri=DAMS.definition_rationale, name="definition_rationale", curie=DAMS.curie('definition_rationale'),
                   model_uri=DAMS.definition_rationale, domain=None, range=Optional[str])

slots.scoped_definitions = Slot(uri=DAMS.scoped_definitions, name="scoped_definitions", curie=DAMS.curie('scoped_definitions'),
                   model_uri=DAMS.scoped_definitions, domain=None, range=Optional[Union[dict[Union[str, ScopedDefinitionScopedDefinitionId], Union[dict, ScopedDefinition]], list[Union[dict, ScopedDefinition]]]])

slots.scoped_definition_id = Slot(uri=DAMS.scoped_definition_id, name="scoped_definition_id", curie=DAMS.curie('scoped_definition_id'),
                   model_uri=DAMS.scoped_definition_id, domain=None, range=URIRef)

slots.scope_kind = Slot(uri=DAMS.scope_kind, name="scope_kind", curie=DAMS.curie('scope_kind'),
                   model_uri=DAMS.scope_kind, domain=None, range=Union[str, "DefinitionScopeKindEnum"])

slots.scope_ref = Slot(uri=DAMS.scope_ref, name="scope_ref", curie=DAMS.curie('scope_ref'),
                   model_uri=DAMS.scope_ref, domain=None, range=Union[str, URIorCURIE])

slots.text = Slot(uri=DAMS.text, name="text", curie=DAMS.curie('text'),
                   model_uri=DAMS.text, domain=None, range=str)

slots.relation_to_reference = Slot(uri=DAMS.relation_to_reference, name="relation_to_reference", curie=DAMS.curie('relation_to_reference'),
                   model_uri=DAMS.relation_to_reference, domain=None, range=Union[str, "ScopedDefinitionRelationEnum"])

slots.rationale = Slot(uri=DAMS.rationale, name="rationale", curie=DAMS.curie('rationale'),
                   model_uri=DAMS.rationale, domain=None, range=Optional[str])

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

slots.mappings = Slot(uri=DAMS.mappings, name="mappings", curie=DAMS.curie('mappings'),
                   model_uri=DAMS.mappings, domain=None, range=Optional[Union[dict[Union[str, MappingElementId], Union[dict, Mapping]], list[Union[dict, Mapping]]]])

slots.data_carriers = Slot(uri=DAMS.data_carriers, name="data_carriers", curie=DAMS.curie('data_carriers'),
                   model_uri=DAMS.data_carriers, domain=None, range=Optional[Union[dict[Union[str, DataCarrierElementId], Union[dict, DataCarrier]], list[Union[dict, DataCarrier]]]])

slots.access_points = Slot(uri=DAMS.access_points, name="access_points", curie=DAMS.curie('access_points'),
                   model_uri=DAMS.access_points, domain=None, range=Optional[Union[dict[Union[str, AccessPointElementId], Union[dict, AccessPoint]], list[Union[dict, AccessPoint]]]])

slots.data_containers = Slot(uri=DAMS.data_containers, name="data_containers", curie=DAMS.curie('data_containers'),
                   model_uri=DAMS.data_containers, domain=None, range=Optional[Union[dict[Union[str, DataContainerElementId], Union[dict, DataContainer]], list[Union[dict, DataContainer]]]])

slots.execution_assets = Slot(uri=DAMS.execution_assets, name="execution_assets", curie=DAMS.curie('execution_assets'),
                   model_uri=DAMS.execution_assets, domain=None, range=Optional[Union[dict[Union[str, ExecutionAssetElementId], Union[dict, ExecutionAsset]], list[Union[dict, ExecutionAsset]]]])

slots.conceptual_properties = Slot(uri=DAMS.conceptual_properties, name="conceptual_properties", curie=DAMS.curie('conceptual_properties'),
                   model_uri=DAMS.conceptual_properties, domain=None, range=Optional[Union[dict[Union[str, ConceptualPropertyElementId], Union[dict, ConceptualProperty]], list[Union[dict, ConceptualProperty]]]])

slots.conceptual_domains = Slot(uri=DAMS.conceptual_domains, name="conceptual_domains", curie=DAMS.curie('conceptual_domains'),
                   model_uri=DAMS.conceptual_domains, domain=None, range=Optional[Union[dict[Union[str, ConceptualDomainElementId], Union[dict, ConceptualDomain]], list[Union[dict, ConceptualDomain]]]])

slots.value_domains = Slot(uri=DAMS.value_domains, name="value_domains", curie=DAMS.curie('value_domains'),
                   model_uri=DAMS.value_domains, domain=None, range=Optional[Union[dict[Union[str, ValueDomainElementId], Union[dict, ValueDomain]], list[Union[dict, ValueDomain]]]])

slots.data_types = Slot(uri=DAMS.data_types, name="data_types", curie=DAMS.curie('data_types'),
                   model_uri=DAMS.data_types, domain=None, range=Optional[Union[dict[Union[str, DataTypeElementId], Union[dict, DataType]], list[Union[dict, DataType]]]])

slots.native_type_bindings = Slot(uri=DAMS.native_type_bindings, name="native_type_bindings", curie=DAMS.curie('native_type_bindings'),
                   model_uri=DAMS.native_type_bindings, domain=None, range=Optional[Union[dict[Union[str, NativeTypeBindingBindingId], Union[dict, NativeTypeBinding]], list[Union[dict, NativeTypeBinding]]]])

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

slots.entity_tier = Slot(uri=DAMS.entity_tier, name="entity_tier", curie=DAMS.curie('entity_tier'),
                   model_uri=DAMS.entity_tier, domain=None, range=Optional[Union[str, "EntityTierEnum"]])

slots.dependency_kind = Slot(uri=DAMS.dependency_kind, name="dependency_kind", curie=DAMS.curie('dependency_kind'),
                   model_uri=DAMS.dependency_kind, domain=None, range=Optional[Union[str, "DependencyKindEnum"]])

slots.depends_on_refs = Slot(uri=DAMS.depends_on_refs, name="depends_on_refs", curie=DAMS.curie('depends_on_refs'),
                   model_uri=DAMS.depends_on_refs, domain=None, range=Optional[Union[Union[str, ConceptualEntityElementId], list[Union[str, ConceptualEntityElementId]]]])

slots.genesis_kind = Slot(uri=DAMS.genesis_kind, name="genesis_kind", curie=DAMS.curie('genesis_kind'),
                   model_uri=DAMS.genesis_kind, domain=None, range=Optional[Union[str, "GenesisKindEnum"]])

slots.external_class_refs = Slot(uri=DAMS.external_class_refs, name="external_class_refs", curie=DAMS.curie('external_class_refs'),
                   model_uri=DAMS.external_class_refs, domain=None, range=Optional[Union[dict[Union[str, ExternalClassRefExternalClassRefId], Union[dict, ExternalClassRef]], list[Union[dict, ExternalClassRef]]]])

slots.relation_terms = Slot(uri=DAMS.relation_terms, name="relation_terms", curie=DAMS.curie('relation_terms'),
                   model_uri=DAMS.relation_terms, domain=None, range=Optional[Union[dict[Union[str, RelationTermElementId], Union[dict, RelationTerm]], list[Union[dict, RelationTerm]]]])

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

slots.property_owner_entity_ref = Slot(uri=DAMS.property_owner_entity_ref, name="property_owner_entity_ref", curie=DAMS.curie('property_owner_entity_ref'),
                   model_uri=DAMS.property_owner_entity_ref, domain=None, range=Union[str, ConceptualEntityElementId])

slots.concept_ref = Slot(uri=DAMS.concept_ref, name="concept_ref", curie=DAMS.curie('concept_ref'),
                   model_uri=DAMS.concept_ref, domain=None, range=Optional[Union[str, ConceptualPropertyElementId]])

slots.value_domain_ref = Slot(uri=DAMS.value_domain_ref, name="value_domain_ref", curie=DAMS.curie('value_domain_ref'),
                   model_uri=DAMS.value_domain_ref, domain=None, range=Optional[Union[str, ValueDomainElementId]])

slots.critical_data_element = Slot(uri=DAMS.critical_data_element, name="critical_data_element", curie=DAMS.curie('critical_data_element'),
                   model_uri=DAMS.critical_data_element, domain=None, range=Optional[Union[bool, Bool]])

slots.significance_basis = Slot(uri=DAMS.significance_basis, name="significance_basis", curie=DAMS.curie('significance_basis'),
                   model_uri=DAMS.significance_basis, domain=None, range=Union[Union[str, "SignificanceBasisEnum"], list[Union[str, "SignificanceBasisEnum"]]])

slots.significance_rationale = Slot(uri=DAMS.significance_rationale, name="significance_rationale", curie=DAMS.curie('significance_rationale'),
                   model_uri=DAMS.significance_rationale, domain=None, range=Optional[str])

slots.property_kind = Slot(uri=DAMS.property_kind, name="property_kind", curie=DAMS.curie('property_kind'),
                   model_uri=DAMS.property_kind, domain=None, range=Union[str, "PropertyKindEnum"])

slots.is_identifying = Slot(uri=DAMS.is_identifying, name="is_identifying", curie=DAMS.curie('is_identifying'),
                   model_uri=DAMS.is_identifying, domain=None, range=Optional[Union[bool, Bool]])

slots.required = Slot(uri=DAMS.required, name="required", curie=DAMS.curie('required'),
                   model_uri=DAMS.required, domain=None, range=Union[bool, Bool])

slots.multivalued = Slot(uri=DAMS.multivalued, name="multivalued", curie=DAMS.curie('multivalued'),
                   model_uri=DAMS.multivalued, domain=None, range=Union[bool, Bool])

slots.minimum_cardinality = Slot(uri=DAMS.minimum_cardinality, name="minimum_cardinality", curie=DAMS.curie('minimum_cardinality'),
                   model_uri=DAMS.minimum_cardinality, domain=None, range=Optional[int])

slots.maximum_cardinality = Slot(uri=DAMS.maximum_cardinality, name="maximum_cardinality", curie=DAMS.curie('maximum_cardinality'),
                   model_uri=DAMS.maximum_cardinality, domain=None, range=Optional[int])

slots.default_value = Slot(uri=DAMS.default_value, name="default_value", curie=DAMS.curie('default_value'),
                   model_uri=DAMS.default_value, domain=None, range=Optional[str])

slots.derived_expression = Slot(uri=DAMS.derived_expression, name="derived_expression", curie=DAMS.curie('derived_expression'),
                   model_uri=DAMS.derived_expression, domain=None, range=Optional[str])

slots.identity_rule = Slot(uri=DAMS.identity_rule, name="identity_rule", curie=DAMS.curie('identity_rule'),
                   model_uri=DAMS.identity_rule, domain=None, range=Optional[str])

slots.business_key_kind = Slot(uri=DAMS.business_key_kind, name="business_key_kind", curie=DAMS.curie('business_key_kind'),
                   model_uri=DAMS.business_key_kind, domain=None, range=Optional[Union[str, "BusinessKeyKindEnum"]])

slots.conceptual_alignment_status = Slot(uri=DAMS.conceptual_alignment_status, name="conceptual_alignment_status", curie=DAMS.curie('conceptual_alignment_status'),
                   model_uri=DAMS.conceptual_alignment_status, domain=None, range=Optional[Union[str, "ConceptualAlignmentStatusEnum"]])

slots.alignment_rationale = Slot(uri=DAMS.alignment_rationale, name="alignment_rationale", curie=DAMS.curie('alignment_rationale'),
                   model_uri=DAMS.alignment_rationale, domain=None, range=Optional[str])

slots.isolation_rationale = Slot(uri=DAMS.isolation_rationale, name="isolation_rationale", curie=DAMS.curie('isolation_rationale'),
                   model_uri=DAMS.isolation_rationale, domain=None, range=Optional[str])

slots.mapping_coverage_status = Slot(uri=DAMS.mapping_coverage_status, name="mapping_coverage_status", curie=DAMS.curie('mapping_coverage_status'),
                   model_uri=DAMS.mapping_coverage_status, domain=None, range=Optional[Union[str, "MappingCoverageStatusEnum"]])

slots.mapping_rationale = Slot(uri=DAMS.mapping_rationale, name="mapping_rationale", curie=DAMS.curie('mapping_rationale'),
                   model_uri=DAMS.mapping_rationale, domain=None, range=Optional[str])

slots.currency_attribute_ref = Slot(uri=DAMS.currency_attribute_ref, name="currency_attribute_ref", curie=DAMS.curie('currency_attribute_ref'),
                   model_uri=DAMS.currency_attribute_ref, domain=None, range=Optional[Union[str, URIorCURIE]])

slots.timezone_policy = Slot(uri=DAMS.timezone_policy, name="timezone_policy", curie=DAMS.curie('timezone_policy'),
                   model_uri=DAMS.timezone_policy, domain=None, range=Optional[str])

slots.temporal_semantics = Slot(uri=DAMS.temporal_semantics, name="temporal_semantics", curie=DAMS.curie('temporal_semantics'),
                   model_uri=DAMS.temporal_semantics, domain=None, range=Optional[str])

slots.relationship_kind = Slot(uri=DAMS.relationship_kind, name="relationship_kind", curie=DAMS.curie('relationship_kind'),
                   model_uri=DAMS.relationship_kind, domain=None, range=Optional[Union[str, "RelationshipKindEnum"]])

slots.cardinality_rationale = Slot(uri=DAMS.cardinality_rationale, name="cardinality_rationale", curie=DAMS.curie('cardinality_rationale'),
                   model_uri=DAMS.cardinality_rationale, domain=None, range=Optional[str])

slots.relation_term_ref = Slot(uri=DAMS.relation_term_ref, name="relation_term_ref", curie=DAMS.curie('relation_term_ref'),
                   model_uri=DAMS.relation_term_ref, domain=None, range=Optional[Union[str, RelationTermElementId]])

slots.term_direction = Slot(uri=DAMS.term_direction, name="term_direction", curie=DAMS.curie('term_direction'),
                   model_uri=DAMS.term_direction, domain=None, range=Optional[Union[str, "TermDirectionEnum"]])

slots.forward_label = Slot(uri=DAMS.forward_label, name="forward_label", curie=DAMS.curie('forward_label'),
                   model_uri=DAMS.forward_label, domain=None, range=str)

slots.forward_label_en = Slot(uri=DAMS.forward_label_en, name="forward_label_en", curie=DAMS.curie('forward_label_en'),
                   model_uri=DAMS.forward_label_en, domain=None, range=Optional[str])

slots.inverse_label = Slot(uri=DAMS.inverse_label, name="inverse_label", curie=DAMS.curie('inverse_label'),
                   model_uri=DAMS.inverse_label, domain=None, range=Optional[str])

slots.inverse_label_en = Slot(uri=DAMS.inverse_label_en, name="inverse_label_en", curie=DAMS.curie('inverse_label_en'),
                   model_uri=DAMS.inverse_label_en, domain=None, range=Optional[str])

slots.symmetric = Slot(uri=DAMS.symmetric, name="symmetric", curie=DAMS.curie('symmetric'),
                   model_uri=DAMS.symmetric, domain=None, range=Optional[Union[bool, Bool]])

slots.default_relationship_kind = Slot(uri=DAMS.default_relationship_kind, name="default_relationship_kind", curie=DAMS.curie('default_relationship_kind'),
                   model_uri=DAMS.default_relationship_kind, domain=None, range=Optional[Union[str, "RelationshipKindEnum"]])

slots.ontology_property_ref = Slot(uri=DAMS.ontology_property_ref, name="ontology_property_ref", curie=DAMS.curie('ontology_property_ref'),
                   model_uri=DAMS.ontology_property_ref, domain=None, range=Optional[Union[str, URIorCURIE]])

slots.external_class_ref_id = Slot(uri=DAMS.external_class_ref_id, name="external_class_ref_id", curie=DAMS.curie('external_class_ref_id'),
                   model_uri=DAMS.external_class_ref_id, domain=None, range=URIRef)

slots.target_ref = Slot(uri=DAMS.target_ref, name="target_ref", curie=DAMS.curie('target_ref'),
                   model_uri=DAMS.target_ref, domain=None, range=Union[str, URIorCURIE])

slots.match_kind = Slot(uri=DAMS.match_kind, name="match_kind", curie=DAMS.curie('match_kind'),
                   model_uri=DAMS.match_kind, domain=None, range=Union[str, "ExternalMatchKindEnum"])

slots.source_kind = Slot(uri=DAMS.source_kind, name="source_kind", curie=DAMS.curie('source_kind'),
                   model_uri=DAMS.source_kind, domain=None, range=Union[str, "ExternalSourceKindEnum"])

slots.external_specification_ref = Slot(uri=DAMS.external_specification_ref, name="external_specification_ref", curie=DAMS.curie('external_specification_ref'),
                   model_uri=DAMS.external_specification_ref, domain=None, range=Optional[Union[str, URIorCURIE]])

slots.selection_ref = Slot(uri=DAMS.selection_ref, name="selection_ref", curie=DAMS.curie('selection_ref'),
                   model_uri=DAMS.selection_ref, domain=None, range=Optional[Union[str, URIorCURIE]])

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

slots.qualified_name = Slot(uri=DAMS.qualified_name, name="qualified_name", curie=DAMS.curie('qualified_name'),
                   model_uri=DAMS.qualified_name, domain=None, range=str)

slots.technology = Slot(uri=DAMS.technology, name="technology", curie=DAMS.curie('technology'),
                   model_uri=DAMS.technology, domain=None, range=Optional[str])

slots.direction = Slot(uri=DAMS.direction, name="direction", curie=DAMS.curie('direction'),
                   model_uri=DAMS.direction, domain=None, range=Optional[Union[str, "FlowDirectionEnum"]])

slots.native_name = Slot(uri=DAMS.native_name, name="native_name", curie=DAMS.curie('native_name'),
                   model_uri=DAMS.native_name, domain=None, range=str)

slots.native_type = Slot(uri=DAMS.native_type, name="native_type", curie=DAMS.curie('native_type'),
                   model_uri=DAMS.native_type, domain=None, range=str)

slots.ordinal_position = Slot(uri=DAMS.ordinal_position, name="ordinal_position", curie=DAMS.curie('ordinal_position'),
                   model_uri=DAMS.ordinal_position, domain=None, range=Optional[int])

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

slots.asset_namespace = Slot(uri=DAMS.asset_namespace, name="asset_namespace", curie=DAMS.curie('asset_namespace'),
                   model_uri=DAMS.asset_namespace, domain=None, range=str)

slots.parent_ref = Slot(uri=DAMS.parent_ref, name="parent_ref", curie=DAMS.curie('parent_ref'),
                   model_uri=DAMS.parent_ref, domain=None, range=Optional[Union[str, TechnicalAssetElementId]])

slots.asset_kind = Slot(uri=DAMS.asset_kind, name="asset_kind", curie=DAMS.curie('asset_kind'),
                   model_uri=DAMS.asset_kind, domain=None, range=str)

slots.lineage_role = Slot(uri=DAMS.lineage_role, name="lineage_role", curie=DAMS.curie('lineage_role'),
                   model_uri=DAMS.lineage_role, domain=None, range=Optional[Union[str, "LineageRoleEnum"]])

slots.structure_ref = Slot(uri=DAMS.structure_ref, name="structure_ref", curie=DAMS.curie('structure_ref'),
                   model_uri=DAMS.structure_ref, domain=None, range=Optional[Union[str, DataStructureElementId]])

slots.data_format = Slot(uri=DAMS.data_format, name="data_format", curie=DAMS.curie('data_format'),
                   model_uri=DAMS.data_format, domain=None, range=Optional[str])

slots.protocol = Slot(uri=DAMS.protocol, name="protocol", curie=DAMS.curie('protocol'),
                   model_uri=DAMS.protocol, domain=None, range=Optional[str])

slots.protocol_version = Slot(uri=DAMS.protocol_version, name="protocol_version", curie=DAMS.curie('protocol_version'),
                   model_uri=DAMS.protocol_version, domain=None, range=Optional[str])

slots.binding_ref = Slot(uri=DAMS.binding_ref, name="binding_ref", curie=DAMS.curie('binding_ref'),
                   model_uri=DAMS.binding_ref, domain=None, range=Optional[Union[str, URIorCURIE]])

slots.containment_kind = Slot(uri=DAMS.containment_kind, name="containment_kind", curie=DAMS.curie('containment_kind'),
                   model_uri=DAMS.containment_kind, domain=None, range=Optional[Union[str, "ContainmentKindEnum"]])

slots.location_uri = Slot(uri=DAMS.location_uri, name="location_uri", curie=DAMS.curie('location_uri'),
                   model_uri=DAMS.location_uri, domain=None, range=Optional[Union[str, URI]])

slots.region = Slot(uri=DAMS.region, name="region", curie=DAMS.curie('region'),
                   model_uri=DAMS.region, domain=None, range=Optional[str])

slots.serves_refs = Slot(uri=DAMS.serves_refs, name="serves_refs", curie=DAMS.curie('serves_refs'),
                   model_uri=DAMS.serves_refs, domain=None, range=Optional[Union[Union[str, DataCarrierElementId], list[Union[str, DataCarrierElementId]]]])

slots.interface_ref = Slot(uri=DAMS.interface_ref, name="interface_ref", curie=DAMS.curie('interface_ref'),
                   model_uri=DAMS.interface_ref, domain=None, range=Optional[Union[str, AccessPointElementId]])

slots.operation_name = Slot(uri=DAMS.operation_name, name="operation_name", curie=DAMS.curie('operation_name'),
                   model_uri=DAMS.operation_name, domain=None, range=Optional[str])

slots.http_method = Slot(uri=DAMS.http_method, name="http_method", curie=DAMS.curie('http_method'),
                   model_uri=DAMS.http_method, domain=None, range=Optional[str])

slots.path_template = Slot(uri=DAMS.path_template, name="path_template", curie=DAMS.curie('path_template'),
                   model_uri=DAMS.path_template, domain=None, range=Optional[str])

slots.produces_refs = Slot(uri=DAMS.produces_refs, name="produces_refs", curie=DAMS.curie('produces_refs'),
                   model_uri=DAMS.produces_refs, domain=None, range=Optional[Union[Union[str, TechnicalAssetElementId], list[Union[str, TechnicalAssetElementId]]]])

slots.consumes_refs = Slot(uri=DAMS.consumes_refs, name="consumes_refs", curie=DAMS.curie('consumes_refs'),
                   model_uri=DAMS.consumes_refs, domain=None, range=Optional[Union[Union[str, TechnicalAssetElementId], list[Union[str, TechnicalAssetElementId]]]])

slots.conceptual_domain_kind = Slot(uri=DAMS.conceptual_domain_kind, name="conceptual_domain_kind", curie=DAMS.curie('conceptual_domain_kind'),
                   model_uri=DAMS.conceptual_domain_kind, domain=None, range=Union[str, "ConceptualDomainKindEnum"])

slots.value_meanings = Slot(uri=DAMS.value_meanings, name="value_meanings", curie=DAMS.curie('value_meanings'),
                   model_uri=DAMS.value_meanings, domain=None, range=Optional[Union[dict[Union[str, ValueMeaningMeaningKey], Union[dict, ValueMeaning]], list[Union[dict, ValueMeaning]]]])

slots.concept_scheme_uri = Slot(uri=DAMS.concept_scheme_uri, name="concept_scheme_uri", curie=DAMS.curie('concept_scheme_uri'),
                   model_uri=DAMS.concept_scheme_uri, domain=None, range=Optional[Union[str, URIorCURIE]])

slots.broader_domain_ref = Slot(uri=DAMS.broader_domain_ref, name="broader_domain_ref", curie=DAMS.curie('broader_domain_ref'),
                   model_uri=DAMS.broader_domain_ref, domain=None, range=Optional[Union[str, ConceptualDomainElementId]])

slots.meaning_key = Slot(uri=DAMS.meaning_key, name="meaning_key", curie=DAMS.curie('meaning_key'),
                   model_uri=DAMS.meaning_key, domain=None, range=URIRef)

slots.meaning_label = Slot(uri=DAMS.meaning_label, name="meaning_label", curie=DAMS.curie('meaning_label'),
                   model_uri=DAMS.meaning_label, domain=None, range=Optional[str])

slots.meaning_definition = Slot(uri=DAMS.meaning_definition, name="meaning_definition", curie=DAMS.curie('meaning_definition'),
                   model_uri=DAMS.meaning_definition, domain=None, range=Optional[str])

slots.meaning_term_ref = Slot(uri=DAMS.meaning_term_ref, name="meaning_term_ref", curie=DAMS.curie('meaning_term_ref'),
                   model_uri=DAMS.meaning_term_ref, domain=None, range=Optional[Union[str, URIorCURIE]])

slots.broader_meaning_key = Slot(uri=DAMS.broader_meaning_key, name="broader_meaning_key", curie=DAMS.curie('broader_meaning_key'),
                   model_uri=DAMS.broader_meaning_key, domain=None, range=Optional[str])

slots.meaning_status = Slot(uri=DAMS.meaning_status, name="meaning_status", curie=DAMS.curie('meaning_status'),
                   model_uri=DAMS.meaning_status, domain=None, range=Optional[Union[str, "LifecycleStatusEnum"]])

slots.type_name = Slot(uri=DAMS.type_name, name="type_name", curie=DAMS.curie('type_name'),
                   model_uri=DAMS.type_name, domain=None, range=str)

slots.type_family = Slot(uri=DAMS.type_family, name="type_family", curie=DAMS.curie('type_family'),
                   model_uri=DAMS.type_family, domain=None, range=Union[str, "TypeFamilyEnum"])

slots.precision = Slot(uri=DAMS.precision, name="precision", curie=DAMS.curie('precision'),
                   model_uri=DAMS.precision, domain=None, range=Optional[int])

slots.scale = Slot(uri=DAMS.scale, name="scale", curie=DAMS.curie('scale'),
                   model_uri=DAMS.scale, domain=None, range=Optional[int])

slots.max_length = Slot(uri=DAMS.max_length, name="max_length", curie=DAMS.curie('max_length'),
                   model_uri=DAMS.max_length, domain=None, range=Optional[int])

slots.min_length = Slot(uri=DAMS.min_length, name="min_length", curie=DAMS.curie('min_length'),
                   model_uri=DAMS.min_length, domain=None, range=Optional[int])

slots.datatype_timezone_policy = Slot(uri=DAMS.datatype_timezone_policy, name="datatype_timezone_policy", curie=DAMS.curie('datatype_timezone_policy'),
                   model_uri=DAMS.datatype_timezone_policy, domain=None, range=Optional[Union[str, "TimezonePolicyEnum"]])

slots.charset = Slot(uri=DAMS.charset, name="charset", curie=DAMS.curie('charset'),
                   model_uri=DAMS.charset, domain=None, range=Optional[str])

slots.xsd_datatype = Slot(uri=DAMS.xsd_datatype, name="xsd_datatype", curie=DAMS.curie('xsd_datatype'),
                   model_uri=DAMS.xsd_datatype, domain=None, range=Optional[Union[str, URIorCURIE]])

slots.linkml_type = Slot(uri=DAMS.linkml_type, name="linkml_type", curie=DAMS.curie('linkml_type'),
                   model_uri=DAMS.linkml_type, domain=None, range=Optional[str])

slots.base_type_ref = Slot(uri=DAMS.base_type_ref, name="base_type_ref", curie=DAMS.curie('base_type_ref'),
                   model_uri=DAMS.base_type_ref, domain=None, range=Optional[Union[str, DataTypeElementId]])

slots.binding_id = Slot(uri=DAMS.binding_id, name="binding_id", curie=DAMS.curie('binding_id'),
                   model_uri=DAMS.binding_id, domain=None, range=URIRef)

slots.dialect = Slot(uri=DAMS.dialect, name="dialect", curie=DAMS.curie('dialect'),
                   model_uri=DAMS.dialect, domain=None, range=str)

slots.dialect_native_type = Slot(uri=DAMS.dialect_native_type, name="dialect_native_type", curie=DAMS.curie('dialect_native_type'),
                   model_uri=DAMS.dialect_native_type, domain=None, range=str)

slots.data_type_ref = Slot(uri=DAMS.data_type_ref, name="data_type_ref", curie=DAMS.curie('data_type_ref'),
                   model_uri=DAMS.data_type_ref, domain=None, range=Optional[Union[str, DataTypeElementId]])

slots.unit_code = Slot(uri=DAMS.unit_code, name="unit_code", curie=DAMS.curie('unit_code'),
                   model_uri=DAMS.unit_code, domain=None, range=Optional[str])

slots.format_pattern = Slot(uri=DAMS.format_pattern, name="format_pattern", curie=DAMS.curie('format_pattern'),
                   model_uri=DAMS.format_pattern, domain=None, range=Optional[str])

slots.lossiness = Slot(uri=DAMS.lossiness, name="lossiness", curie=DAMS.curie('lossiness'),
                   model_uri=DAMS.lossiness, domain=None, range=Union[str, "LossinessEnum"])

slots.parameter_mapping = Slot(uri=DAMS.parameter_mapping, name="parameter_mapping", curie=DAMS.curie('parameter_mapping'),
                   model_uri=DAMS.parameter_mapping, domain=None, range=Optional[str])

slots.value_domain_kind = Slot(uri=DAMS.value_domain_kind, name="value_domain_kind", curie=DAMS.curie('value_domain_kind'),
                   model_uri=DAMS.value_domain_kind, domain=None, range=Union[str, "ValueDomainKindEnum"])

slots.conceptual_domain_ref = Slot(uri=DAMS.conceptual_domain_ref, name="conceptual_domain_ref", curie=DAMS.curie('conceptual_domain_ref'),
                   model_uri=DAMS.conceptual_domain_ref, domain=None, range=Optional[Union[str, ConceptualDomainElementId]])

slots.min_value = Slot(uri=DAMS.min_value, name="min_value", curie=DAMS.curie('min_value'),
                   model_uri=DAMS.min_value, domain=None, range=Optional[str])

slots.max_value = Slot(uri=DAMS.max_value, name="max_value", curie=DAMS.curie('max_value'),
                   model_uri=DAMS.max_value, domain=None, range=Optional[str])

slots.permissible_values = Slot(uri=DAMS.permissible_values, name="permissible_values", curie=DAMS.curie('permissible_values'),
                   model_uri=DAMS.permissible_values, domain=None, range=Optional[Union[dict[Union[str, PermissibleValueValueCode], Union[dict, PermissibleValue]], list[Union[dict, PermissibleValue]]]])

slots.value_set_source = Slot(uri=DAMS.value_set_source, name="value_set_source", curie=DAMS.curie('value_set_source'),
                   model_uri=DAMS.value_set_source, domain=None, range=Optional[Union[str, URIorCURIE]])

slots.dynamic_query = Slot(uri=DAMS.dynamic_query, name="dynamic_query", curie=DAMS.curie('dynamic_query'),
                   model_uri=DAMS.dynamic_query, domain=None, range=Optional[Union[dict, ValueSetQuery]])

slots.value_code = Slot(uri=DAMS.value_code, name="value_code", curie=DAMS.curie('value_code'),
                   model_uri=DAMS.value_code, domain=None, range=URIRef)

slots.value_label = Slot(uri=DAMS.value_label, name="value_label", curie=DAMS.curie('value_label'),
                   model_uri=DAMS.value_label, domain=None, range=Optional[str])

slots.value_definition = Slot(uri=DAMS.value_definition, name="value_definition", curie=DAMS.curie('value_definition'),
                   model_uri=DAMS.value_definition, domain=None, range=Optional[str])

slots.value_meaning_key = Slot(uri=DAMS.value_meaning_key, name="value_meaning_key", curie=DAMS.curie('value_meaning_key'),
                   model_uri=DAMS.value_meaning_key, domain=None, range=Optional[str])

slots.ordinal = Slot(uri=DAMS.ordinal, name="ordinal", curie=DAMS.curie('ordinal'),
                   model_uri=DAMS.ordinal, domain=None, range=Optional[int])

slots.value_status = Slot(uri=DAMS.value_status, name="value_status", curie=DAMS.curie('value_status'),
                   model_uri=DAMS.value_status, domain=None, range=Optional[Union[str, "LifecycleStatusEnum"]])

slots.value_set_query_id = Slot(uri=DAMS.value_set_query_id, name="value_set_query_id", curie=DAMS.curie('value_set_query_id'),
                   model_uri=DAMS.value_set_query_id, domain=None, range=URIRef)

slots.source_ontology = Slot(uri=DAMS.source_ontology, name="source_ontology", curie=DAMS.curie('source_ontology'),
                   model_uri=DAMS.source_ontology, domain=None, range=Union[str, URIorCURIE])

slots.source_nodes = Slot(uri=DAMS.source_nodes, name="source_nodes", curie=DAMS.curie('source_nodes'),
                   model_uri=DAMS.source_nodes, domain=None, range=Optional[Union[Union[str, URIorCURIE], list[Union[str, URIorCURIE]]]])

slots.relationship_types = Slot(uri=DAMS.relationship_types, name="relationship_types", curie=DAMS.curie('relationship_types'),
                   model_uri=DAMS.relationship_types, domain=None, range=Optional[Union[Union[str, URIorCURIE], list[Union[str, URIorCURIE]]]])

slots.include_self = Slot(uri=DAMS.include_self, name="include_self", curie=DAMS.curie('include_self'),
                   model_uri=DAMS.include_self, domain=None, range=Optional[Union[bool, Bool]])

slots.local_key = Slot(uri=DAMS.local_key, name="local_key", curie=DAMS.curie('local_key'),
                   model_uri=DAMS.local_key, domain=None, range=URIRef)

slots.schema_format = Slot(uri=DAMS.schema_format, name="schema_format", curie=DAMS.curie('schema_format'),
                   model_uri=DAMS.schema_format, domain=None, range=Union[str, "SchemaFormatEnum"])

slots.schema_dialect = Slot(uri=DAMS.schema_dialect, name="schema_dialect", curie=DAMS.curie('schema_dialect'),
                   model_uri=DAMS.schema_dialect, domain=None, range=Optional[Union[str, URI]])

slots.structure_version = Slot(uri=DAMS.structure_version, name="structure_version", curie=DAMS.curie('structure_version'),
                   model_uri=DAMS.structure_version, domain=None, range=Union[str, SemVer])

slots.root_local_key = Slot(uri=DAMS.root_local_key, name="root_local_key", curie=DAMS.curie('root_local_key'),
                   model_uri=DAMS.root_local_key, domain=None, range=str,
                   pattern=re.compile(r'^[a-z0-9_.-]+$'))

slots.nodes = Slot(uri=DAMS.nodes, name="nodes", curie=DAMS.curie('nodes'),
                   model_uri=DAMS.nodes, domain=None, range=Union[dict[Union[str, SchemaNodeLocalKey], Union[dict, SchemaNode]], list[Union[dict, SchemaNode]]])

slots.source_pointer = Slot(uri=DAMS.source_pointer, name="source_pointer", curie=DAMS.curie('source_pointer'),
                   model_uri=DAMS.source_pointer, domain=None, range=Optional[str])

slots.content_digest = Slot(uri=DAMS.content_digest, name="content_digest", curie=DAMS.curie('content_digest'),
                   model_uri=DAMS.content_digest, domain=None, range=Optional[Union[str, Sha256Digest]])

slots.previous_version_ref = Slot(uri=DAMS.previous_version_ref, name="previous_version_ref", curie=DAMS.curie('previous_version_ref'),
                   model_uri=DAMS.previous_version_ref, domain=None, range=Optional[Union[str, DataStructureElementId]])

slots.node_kind = Slot(uri=DAMS.node_kind, name="node_kind", curie=DAMS.curie('node_kind'),
                   model_uri=DAMS.node_kind, domain=None, range=Union[str, "SchemaNodeKindEnum"])

slots.children = Slot(uri=DAMS.children, name="children", curie=DAMS.curie('children'),
                   model_uri=DAMS.children, domain=None, range=Optional[Union[str, list[str]]])

slots.item_node = Slot(uri=DAMS.item_node, name="item_node", curie=DAMS.curie('item_node'),
                   model_uri=DAMS.item_node, domain=None, range=Optional[str])

slots.nullable = Slot(uri=DAMS.nullable, name="nullable", curie=DAMS.curie('nullable'),
                   model_uri=DAMS.nullable, domain=None, range=Optional[Union[bool, Bool]])

slots.min_occurs = Slot(uri=DAMS.min_occurs, name="min_occurs", curie=DAMS.curie('min_occurs'),
                   model_uri=DAMS.min_occurs, domain=None, range=Optional[int])

slots.max_occurs = Slot(uri=DAMS.max_occurs, name="max_occurs", curie=DAMS.curie('max_occurs'),
                   model_uri=DAMS.max_occurs, domain=None, range=Optional[int])

slots.reference_target = Slot(uri=DAMS.reference_target, name="reference_target", curie=DAMS.curie('reference_target'),
                   model_uri=DAMS.reference_target, domain=None, range=Optional[Union[str, URIorCURIE]])

slots.realizes_attribute_ref = Slot(uri=DAMS.realizes_attribute_ref, name="realizes_attribute_ref", curie=DAMS.curie('realizes_attribute_ref'),
                   model_uri=DAMS.realizes_attribute_ref, domain=None, range=Optional[Union[str, LogicalAttributeElementId]])

slots.constraint_expressions = Slot(uri=DAMS.constraint_expressions, name="constraint_expressions", curie=DAMS.curie('constraint_expressions'),
                   model_uri=DAMS.constraint_expressions, domain=None, range=Optional[Union[str, list[str]]])

slots.column_position = Slot(uri=DAMS.column_position, name="column_position", curie=DAMS.curie('column_position'),
                   model_uri=DAMS.column_position, domain=None, range=Optional[int])

slots.is_primary_key = Slot(uri=DAMS.is_primary_key, name="is_primary_key", curie=DAMS.curie('is_primary_key'),
                   model_uri=DAMS.is_primary_key, domain=None, range=Optional[Union[bool, Bool]])

slots.is_unique = Slot(uri=DAMS.is_unique, name="is_unique", curie=DAMS.curie('is_unique'),
                   model_uri=DAMS.is_unique, domain=None, range=Optional[Union[bool, Bool]])

slots.foreign_key_target = Slot(uri=DAMS.foreign_key_target, name="foreign_key_target", curie=DAMS.curie('foreign_key_target'),
                   model_uri=DAMS.foreign_key_target, domain=None, range=Optional[Union[str, URIorCURIE]])

slots.payload_structure_ref = Slot(uri=DAMS.payload_structure_ref, name="payload_structure_ref", curie=DAMS.curie('payload_structure_ref'),
                   model_uri=DAMS.payload_structure_ref, domain=None, range=Union[str, DataStructureElementId])

slots.headers_structure_ref = Slot(uri=DAMS.headers_structure_ref, name="headers_structure_ref", curie=DAMS.curie('headers_structure_ref'),
                   model_uri=DAMS.headers_structure_ref, domain=None, range=Optional[Union[str, DataStructureElementId]])

slots.content_type = Slot(uri=DAMS.content_type, name="content_type", curie=DAMS.curie('content_type'),
                   model_uri=DAMS.content_type, domain=None, range=Optional[str])

slots.envelope_kind = Slot(uri=DAMS.envelope_kind, name="envelope_kind", curie=DAMS.curie('envelope_kind'),
                   model_uri=DAMS.envelope_kind, domain=None, range=Optional[Union[str, "EnvelopeKindEnum"]])

slots.envelope_ref = Slot(uri=DAMS.envelope_ref, name="envelope_ref", curie=DAMS.curie('envelope_ref'),
                   model_uri=DAMS.envelope_ref, domain=None, range=Optional[Union[str, URIorCURIE]])

slots.correlation_hint = Slot(uri=DAMS.correlation_hint, name="correlation_hint", curie=DAMS.curie('correlation_hint'),
                   model_uri=DAMS.correlation_hint, domain=None, range=Optional[str])

slots.data_structures = Slot(uri=DAMS.data_structures, name="data_structures", curie=DAMS.curie('data_structures'),
                   model_uri=DAMS.data_structures, domain=None, range=Optional[Union[dict[Union[str, DataStructureElementId], Union[dict, DataStructure]], list[Union[dict, DataStructure]]]])

slots.messages = Slot(uri=DAMS.messages, name="messages", curie=DAMS.curie('messages'),
                   model_uri=DAMS.messages, domain=None, range=Optional[Union[dict[Union[str, MessageElementId], Union[dict, Message]], list[Union[dict, Message]]]])

slots.message_refs = Slot(uri=DAMS.message_refs, name="message_refs", curie=DAMS.curie('message_refs'),
                   model_uri=DAMS.message_refs, domain=None, range=Optional[Union[Union[str, MessageElementId], list[Union[str, MessageElementId]]]])

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

slots.carrier_refs = Slot(uri=DAMS.carrier_refs, name="carrier_refs", curie=DAMS.curie('carrier_refs'),
                   model_uri=DAMS.carrier_refs, domain=None, range=Optional[Union[Union[str, DataCarrierElementId], list[Union[str, DataCarrierElementId]]]])

slots.schema_node_refs = Slot(uri=DAMS.schema_node_refs, name="schema_node_refs", curie=DAMS.curie('schema_node_refs'),
                   model_uri=DAMS.schema_node_refs, domain=None, range=Optional[Union[Union[str, URIorCURIE], list[Union[str, URIorCURIE]]]])

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

slots.applicability_id = Slot(uri=DAMS.applicability_id, name="applicability_id", curie=DAMS.curie('applicability_id'),
                   model_uri=DAMS.applicability_id, domain=None, range=URIRef)

slots.check_id = Slot(uri=DAMS.check_id, name="check_id", curie=DAMS.curie('check_id'),
                   model_uri=DAMS.check_id, domain=None, range=URIRef)

slots.kind = Slot(uri=DAMS.kind, name="kind", curie=DAMS.curie('kind'),
                   model_uri=DAMS.kind, domain=None, range=Union[str, "FormalCheckKindEnum"])

slots.target_class = Slot(uri=DAMS.target_class, name="target_class", curie=DAMS.curie('target_class'),
                   model_uri=DAMS.target_class, domain=None, range=Optional[str])

slots.target_slot = Slot(uri=DAMS.target_slot, name="target_slot", curie=DAMS.curie('target_slot'),
                   model_uri=DAMS.target_slot, domain=None, range=Optional[str])

slots.target_slots = Slot(uri=DAMS.target_slots, name="target_slots", curie=DAMS.curie('target_slots'),
                   model_uri=DAMS.target_slots, domain=None, range=Optional[Union[str, list[str]]])

slots.target_path = Slot(uri=DAMS.target_path, name="target_path", curie=DAMS.curie('target_path'),
                   model_uri=DAMS.target_path, domain=None, range=Optional[str])

slots.severity = Slot(uri=DAMS.severity, name="severity", curie=DAMS.curie('severity'),
                   model_uri=DAMS.severity, domain=None, range=Union[str, "CheckSeverityEnum"])

slots.diagnostic_code = Slot(uri=DAMS.diagnostic_code, name="diagnostic_code", curie=DAMS.curie('diagnostic_code'),
                   model_uri=DAMS.diagnostic_code, domain=None, range=Optional[str])

slots.expression = Slot(uri=DAMS.expression, name="expression", curie=DAMS.curie('expression'),
                   model_uri=DAMS.expression, domain=None, range=Optional[str])

slots.remediation = Slot(uri=DAMS.remediation, name="remediation", curie=DAMS.curie('remediation'),
                   model_uri=DAMS.remediation, domain=None, range=Optional[str])

slots.code = Slot(uri=DAMS.code, name="code", curie=DAMS.curie('code'),
                   model_uri=DAMS.code, domain=None, range=str,
                   pattern=re.compile(r'^(LDM|PDM|REF|ATR|FLW|CLS|GEN)-[0-9]{3}$'))

slots.requirement_level = Slot(uri=DAMS.requirement_level, name="requirement_level", curie=DAMS.curie('requirement_level'),
                   model_uri=DAMS.requirement_level, domain=None, range=Union[str, "RequirementLevelEnum"])

slots.requirement_section = Slot(uri=DAMS.requirement_section, name="requirement_section", curie=DAMS.curie('requirement_section'),
                   model_uri=DAMS.requirement_section, domain=None, range=Union[str, "RequirementSectionEnum"])

slots.statement = Slot(uri=DAMS.statement, name="statement", curie=DAMS.curie('statement'),
                   model_uri=DAMS.statement, domain=None, range=str)

slots.applies_to = Slot(uri=DAMS.applies_to, name="applies_to", curie=DAMS.curie('applies_to'),
                   model_uri=DAMS.applies_to, domain=None, range=Optional[Union[dict, RequirementApplicability]])

slots.applies_target_class = Slot(uri=DAMS.applies_target_class, name="applies_target_class", curie=DAMS.curie('applies_target_class'),
                   model_uri=DAMS.applies_target_class, domain=None, range=Optional[str])

slots.applies_target_kinds = Slot(uri=DAMS.applies_target_kinds, name="applies_target_kinds", curie=DAMS.curie('applies_target_kinds'),
                   model_uri=DAMS.applies_target_kinds, domain=None, range=Optional[Union[str, list[str]]])

slots.applies_implementation_scope = Slot(uri=DAMS.applies_implementation_scope, name="applies_implementation_scope", curie=DAMS.curie('applies_implementation_scope'),
                   model_uri=DAMS.applies_implementation_scope, domain=None, range=Optional[Union[str, "ImplementationScopeEnum"]])

slots.applies_dams_model_level = Slot(uri=DAMS.applies_dams_model_level, name="applies_dams_model_level", curie=DAMS.curie('applies_dams_model_level'),
                   model_uri=DAMS.applies_dams_model_level, domain=None, range=Optional[Union[str, "DAMSModelLevelEnum"]])

slots.applies_implementation_profile = Slot(uri=DAMS.applies_implementation_profile, name="applies_implementation_profile", curie=DAMS.curie('applies_implementation_profile'),
                   model_uri=DAMS.applies_implementation_profile, domain=None, range=Optional[Union[str, "ImplementationProfileEnum"]])

slots.formal_checks = Slot(uri=DAMS.formal_checks, name="formal_checks", curie=DAMS.curie('formal_checks'),
                   model_uri=DAMS.formal_checks, domain=None, range=Optional[Union[dict[Union[str, FormalCheckCheckId], Union[dict, FormalCheck]], list[Union[dict, FormalCheck]]]])

slots.implementation_status = Slot(uri=DAMS.implementation_status, name="implementation_status", curie=DAMS.curie('implementation_status'),
                   model_uri=DAMS.implementation_status, domain=None, range=Optional[Union[str, "RequirementImplementationStatus"]])

slots.superseded_by = Slot(uri=DAMS.superseded_by, name="superseded_by", curie=DAMS.curie('superseded_by'),
                   model_uri=DAMS.superseded_by, domain=None, range=Optional[Union[str, SpecificationRequirementElementId]])

slots.catalog_id = Slot(uri=DAMS.catalog_id, name="catalog_id", curie=DAMS.curie('catalog_id'),
                   model_uri=DAMS.catalog_id, domain=None, range=URIRef)

slots.requirements = Slot(uri=DAMS.requirements, name="requirements", curie=DAMS.curie('requirements'),
                   model_uri=DAMS.requirements, domain=None, range=Optional[Union[dict[Union[str, SpecificationRequirementElementId], Union[dict, SpecificationRequirement]], list[Union[dict, SpecificationRequirement]]]])

slots.HasDefinition_description = Slot(uri=DAMS.description, name="HasDefinition_description", curie=DAMS.curie('description'),
                   model_uri=DAMS.HasDefinition_description, domain=None, range=Optional[str])

slots.ModelPackage_description = Slot(uri=DAMS.description, name="ModelPackage_description", curie=DAMS.curie('description'),
                   model_uri=DAMS.ModelPackage_description, domain=ModelPackage, range=str)

slots.DomainContext_description = Slot(uri=DAMS.description, name="DomainContext_description", curie=DAMS.curie('description'),
                   model_uri=DAMS.DomainContext_description, domain=DomainContext, range=str)

slots.ConceptualProperty_genesis_kind = Slot(uri=DAMS.genesis_kind, name="ConceptualProperty_genesis_kind", curie=DAMS.curie('genesis_kind'),
                   model_uri=DAMS.ConceptualProperty_genesis_kind, domain=ConceptualProperty, range=Union[str, "GenesisKindEnum"])

slots.LogicalAttribute_data_type_ref = Slot(uri=DAMS.data_type_ref, name="LogicalAttribute_data_type_ref", curie=DAMS.curie('data_type_ref'),
                   model_uri=DAMS.LogicalAttribute_data_type_ref, domain=LogicalAttribute, range=Optional[Union[str, DataTypeElementId]])

slots.LogicalAttribute_concept_ref = Slot(uri=DAMS.concept_ref, name="LogicalAttribute_concept_ref", curie=DAMS.curie('concept_ref'),
                   model_uri=DAMS.LogicalAttribute_concept_ref, domain=LogicalAttribute, range=Optional[Union[str, ConceptualPropertyElementId]])

slots.Mapping_name = Slot(uri=DAMS.name, name="Mapping_name", curie=DAMS.curie('name'),
                   model_uri=DAMS.Mapping_name, domain=Mapping, range=str)

slots.Mapping_title = Slot(uri=DAMS.title, name="Mapping_title", curie=DAMS.curie('title'),
                   model_uri=DAMS.Mapping_title, domain=Mapping, range=Optional[str])

slots.Mapping_aliases = Slot(uri=DAMS.aliases, name="Mapping_aliases", curie=DAMS.curie('aliases'),
                   model_uri=DAMS.Mapping_aliases, domain=Mapping, range=Optional[Union[str, list[str]]])

slots.Mapping_glossary_term_refs = Slot(uri=DAMS.glossary_term_refs, name="Mapping_glossary_term_refs", curie=DAMS.curie('glossary_term_refs'),
                   model_uri=DAMS.Mapping_glossary_term_refs, domain=Mapping, range=Optional[Union[Union[str, GlossaryTermRegistryId], list[Union[str, GlossaryTermRegistryId]]]])

slots.Mapping_tags = Slot(uri=DAMS.tags, name="Mapping_tags", curie=DAMS.curie('tags'),
                   model_uri=DAMS.Mapping_tags, domain=Mapping, range=Optional[Union[str, list[str]]])

slots.Mapping_description = Slot(uri=DAMS.description, name="Mapping_description", curie=DAMS.curie('description'),
                   model_uri=DAMS.Mapping_description, domain=Mapping, range=Optional[str])

slots.TechnicalAsset_description = Slot(uri=DAMS.description, name="TechnicalAsset_description", curie=DAMS.curie('description'),
                   model_uri=DAMS.TechnicalAsset_description, domain=TechnicalAsset, range=str)

slots.TechnicalAsset_qualified_name = Slot(uri=DAMS.qualified_name, name="TechnicalAsset_qualified_name", curie=DAMS.curie('qualified_name'),
                   model_uri=DAMS.TechnicalAsset_qualified_name, domain=TechnicalAsset, range=str)

slots.TechnicalAsset_system_ref = Slot(uri=DAMS.system_ref, name="TechnicalAsset_system_ref", curie=DAMS.curie('system_ref'),
                   model_uri=DAMS.TechnicalAsset_system_ref, domain=TechnicalAsset, range=Union[str, ITSystemRegistryId])

slots.TechnicalAsset_native_name = Slot(uri=DAMS.native_name, name="TechnicalAsset_native_name", curie=DAMS.curie('native_name'),
                   model_uri=DAMS.TechnicalAsset_native_name, domain=TechnicalAsset, range=str)

slots.TechnicalAsset_technology = Slot(uri=DAMS.technology, name="TechnicalAsset_technology", curie=DAMS.curie('technology'),
                   model_uri=DAMS.TechnicalAsset_technology, domain=TechnicalAsset, range=Optional[str])

slots.TechnicalAsset_direction = Slot(uri=DAMS.direction, name="TechnicalAsset_direction", curie=DAMS.curie('direction'),
                   model_uri=DAMS.TechnicalAsset_direction, domain=TechnicalAsset, range=Optional[Union[str, "FlowDirectionEnum"]])

slots.DataCarrier_asset_kind = Slot(uri=DAMS.asset_kind, name="DataCarrier_asset_kind", curie=DAMS.curie('asset_kind'),
                   model_uri=DAMS.DataCarrier_asset_kind, domain=DataCarrier, range=Union[str, "DataCarrierKindEnum"])

slots.AccessPoint_asset_kind = Slot(uri=DAMS.asset_kind, name="AccessPoint_asset_kind", curie=DAMS.curie('asset_kind'),
                   model_uri=DAMS.AccessPoint_asset_kind, domain=AccessPoint, range=Union[str, "AccessPointKindEnum"])

slots.AccessPoint_direction = Slot(uri=DAMS.direction, name="AccessPoint_direction", curie=DAMS.curie('direction'),
                   model_uri=DAMS.AccessPoint_direction, domain=AccessPoint, range=Optional[Union[str, "FlowDirectionEnum"]])

slots.DataContainer_asset_kind = Slot(uri=DAMS.asset_kind, name="DataContainer_asset_kind", curie=DAMS.curie('asset_kind'),
                   model_uri=DAMS.DataContainer_asset_kind, domain=DataContainer, range=Union[str, "DataContainerKindEnum"])

slots.DataContainer_direction = Slot(uri=DAMS.direction, name="DataContainer_direction", curie=DAMS.curie('direction'),
                   model_uri=DAMS.DataContainer_direction, domain=DataContainer, range=Optional[Union[str, "FlowDirectionEnum"]])

slots.ExecutionAsset_asset_kind = Slot(uri=DAMS.asset_kind, name="ExecutionAsset_asset_kind", curie=DAMS.curie('asset_kind'),
                   model_uri=DAMS.ExecutionAsset_asset_kind, domain=ExecutionAsset, range=Union[str, "ExecutionAssetKindEnum"])

slots.ExecutionAsset_direction = Slot(uri=DAMS.direction, name="ExecutionAsset_direction", curie=DAMS.curie('direction'),
                   model_uri=DAMS.ExecutionAsset_direction, domain=ExecutionAsset, range=Optional[Union[str, "FlowDirectionEnum"]])

slots.ConceptualDomain_description = Slot(uri=DAMS.description, name="ConceptualDomain_description", curie=DAMS.curie('description'),
                   model_uri=DAMS.ConceptualDomain_description, domain=ConceptualDomain, range=str)

slots.DataType_description = Slot(uri=DAMS.description, name="DataType_description", curie=DAMS.curie('description'),
                   model_uri=DAMS.DataType_description, domain=DataType, range=str)

slots.NativeTypeBinding_data_type_ref = Slot(uri=DAMS.data_type_ref, name="NativeTypeBinding_data_type_ref", curie=DAMS.curie('data_type_ref'),
                   model_uri=DAMS.NativeTypeBinding_data_type_ref, domain=NativeTypeBinding, range=Union[str, DataTypeElementId])

slots.ValueDomain_description = Slot(uri=DAMS.description, name="ValueDomain_description", curie=DAMS.curie('description'),
                   model_uri=DAMS.ValueDomain_description, domain=ValueDomain, range=str)

slots.ValueDomain_data_type_ref = Slot(uri=DAMS.data_type_ref, name="ValueDomain_data_type_ref", curie=DAMS.curie('data_type_ref'),
                   model_uri=DAMS.ValueDomain_data_type_ref, domain=ValueDomain, range=Union[str, DataTypeElementId])

slots.DataStructure_description = Slot(uri=DAMS.description, name="DataStructure_description", curie=DAMS.curie('description'),
                   model_uri=DAMS.DataStructure_description, domain=DataStructure, range=Optional[str])

slots.SchemaNode_native_name = Slot(uri=DAMS.native_name, name="SchemaNode_native_name", curie=DAMS.curie('native_name'),
                   model_uri=DAMS.SchemaNode_native_name, domain=SchemaNode, range=str)

slots.SchemaNode_native_type = Slot(uri=DAMS.native_type, name="SchemaNode_native_type", curie=DAMS.curie('native_type'),
                   model_uri=DAMS.SchemaNode_native_type, domain=SchemaNode, range=str)

slots.SchemaNode_required = Slot(uri=DAMS.required, name="SchemaNode_required", curie=DAMS.curie('required'),
                   model_uri=DAMS.SchemaNode_required, domain=SchemaNode, range=Union[bool, Bool])

slots.SchemaNode_local_key = Slot(uri=DAMS.local_key, name="SchemaNode_local_key", curie=DAMS.curie('local_key'),
                   model_uri=DAMS.SchemaNode_local_key, domain=SchemaNode, range=Union[str, SchemaNodeLocalKey],
                   pattern=re.compile(r'^[a-z0-9_.-]+$'))

slots.DataFlow_description = Slot(uri=DAMS.description, name="DataFlow_description", curie=DAMS.curie('description'),
                   model_uri=DAMS.DataFlow_description, domain=DataFlow, range=str)

slots.DataFlowEntityBinding_description = Slot(uri=DAMS.description, name="DataFlowEntityBinding_description", curie=DAMS.curie('description'),
                   model_uri=DAMS.DataFlowEntityBinding_description, domain=DataFlowEntityBinding, range=str)

slots.DataModelBinding_description = Slot(uri=DAMS.description, name="DataModelBinding_description", curie=DAMS.curie('description'),
                   model_uri=DAMS.DataModelBinding_description, domain=DataModelBinding, range=str)

slots.ModelSelection_description = Slot(uri=DAMS.description, name="ModelSelection_description", curie=DAMS.curie('description'),
                   model_uri=DAMS.ModelSelection_description, domain=ModelSelection, range=str)

slots.SelectedEntity_description = Slot(uri=DAMS.description, name="SelectedEntity_description", curie=DAMS.curie('description'),
                   model_uri=DAMS.SelectedEntity_description, domain=SelectedEntity, range=str)

slots.SelectedAttribute_description = Slot(uri=DAMS.description, name="SelectedAttribute_description", curie=DAMS.curie('description'),
                   model_uri=DAMS.SelectedAttribute_description, domain=SelectedAttribute, range=str)

slots.Metric_description = Slot(uri=DAMS.description, name="Metric_description", curie=DAMS.curie('description'),
                   model_uri=DAMS.Metric_description, domain=Metric, range=str)

slots.Dimension_description = Slot(uri=DAMS.description, name="Dimension_description", curie=DAMS.curie('description'),
                   model_uri=DAMS.Dimension_description, domain=Dimension, range=str)

slots.SpecificationRequirement_description = Slot(uri=DAMS.description, name="SpecificationRequirement_description", curie=DAMS.curie('description'),
                   model_uri=DAMS.SpecificationRequirement_description, domain=SpecificationRequirement, range=str)

slots.SpecificationRequirement_lifecycle_status = Slot(uri=DAMS.lifecycle_status, name="SpecificationRequirement_lifecycle_status", curie=DAMS.curie('lifecycle_status'),
                   model_uri=DAMS.SpecificationRequirement_lifecycle_status, domain=SpecificationRequirement, range=Union[str, "RequirementLifecycleStatus"])
