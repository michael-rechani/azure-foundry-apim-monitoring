"""Rebuild deploy/azuredeploy.json from the workbook JSON.

Run after changing workbooks/PTU-usage-by-APIM-subscription.workbook.json:
    python tools/build_arm_template.py
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
WORKBOOK = ROOT / 'workbooks' / 'PTU-usage-by-APIM-subscription.workbook.json'
TEMPLATE = ROOT / 'deploy' / 'azuredeploy.json'


def main():
    with WORKBOOK.open(encoding='utf-8') as stream:
        workbook = json.load(stream)
    template = {
        '$schema': 'https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#',
        'contentVersion': '1.0.0.0',
        'metadata': {'description': 'Saves the "PTU usage by APIM subscription" workbook in this resource group. '
                                    'It only creates or updates the Workbook resource; it does not change APIM, '
                                    'Azure OpenAI, or Foundry resources.'},
        'parameters': {
            'workbookDisplayName': {
                'type': 'string',
                'defaultValue': 'PTU usage by APIM subscription',
                'metadata': {'description': 'Name shown in Monitor > Workbooks.'},
            },
            'workbookId': {
                'type': 'string',
                'defaultValue': "[guid(resourceGroup().id, parameters('workbookDisplayName'))]",
                'metadata': {'description': 'Deploying again with the same name and resource group updates the same workbook.'},
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
