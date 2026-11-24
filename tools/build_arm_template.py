"""Rebuild deploy/azuredeploy.json from the workbook JSON.

Run after changing workbooks/PTU-usage-by-APIM-subscription.workbook.json:
    python tools/build_arm_template.py
"""

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
WORKBOOK = ROOT / 'workbooks' / 'PTU-usage-by-APIM-subscription.workbook.json'
TEMPLATE = ROOT / 'deploy' / 'azuredeploy.json'


def workbook_version(workbook):
    match = re.search(r'Workbook version: v(\d+\.\d+\.\d+)', json.dumps(workbook))
    if not match:
        raise SystemExit('The workbook intro must contain "Workbook version: vX.Y.Z".')
    return match.group(1)


def main():
    with WORKBOOK.open(encoding='utf-8') as stream:
        workbook = json.load(stream)
    version = workbook_version(workbook)
    template = {
        '$schema': 'https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#',
        'contentVersion': '1.0.0.0',
        'metadata': {'description': 'Saves the "PTU usage by APIM subscription" workbook in this resource group. '
                                    'It creates a new workbook named for this version and does not change APIM, '
                                    'Azure OpenAI, or Foundry resources.'},
        'parameters': {
            'workbookDisplayName': {
                'type': 'string',
                'defaultValue': f'PTU usage by APIM subscription (v{version})',
                'metadata': {'description': 'Name shown in Monitor > Workbooks. Each release has its own default name, '
                                            'so deploying it creates a new workbook and leaves existing copies untouched.'},
            },
            'workbookId': {
                'type': 'string',
                'defaultValue': "[guid(resourceGroup().id, parameters('workbookDisplayName'))]",
                'metadata': {'description': 'Derived from the name and resource group. Deploying the same version again updates that version\'s workbook; a new release creates a separate one.'},
            },
        },
        'resources': [{
            'type': 'Microsoft.Insights/workbooks',
            'apiVersion': '2022-04-01',
            'name': "[parameters('workbookId')]",
            'location': "[resourceGroup().location]",
            'kind': 'shared',
            'properties': {
                'displayName': "[parameters('workbookDisplayName')]",
                'serializedData': json.dumps(workbook, ensure_ascii=False, separators=(',', ':')),
                'version': '1.0',
                'sourceId': 'azure monitor',
                'category': 'workbook',
            },
        }],
        'outputs': {
            'workbookResourceId': {'type': 'string', 'value': "[resourceId('Microsoft.Insights/workbooks', parameters('workbookId'))]"},
        },
    }
    TEMPLATE.parent.mkdir(exist_ok=True)
    with TEMPLATE.open('w', encoding='utf-8', newline='\n') as stream:
        json.dump(template, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print('wrote', TEMPLATE)


if __name__ == '__main__':
    main()
